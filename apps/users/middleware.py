"""
Middleware para isolamento de sessões por aba do navegador.
Permite múltiplas roles/perfis abertos em abas diferentes sem interferência.
"""
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone
from apps.users.models_tab_session import TabSession, TabSessionLog
import uuid


class TabSessionMiddleware(MiddlewareMixin):
    """
    Middleware que fornece isolamento de sessões por aba usando TabId.
    
    Cada aba tem seu próprio tabId (armazenado em sessionStorage no cliente)
    que é enviado via header X-Tab-Id em cada requisição.
    
    Isso permite que múltiplas abas tenham sessões diferentes do mesmo usuário.
    """
    
    def process_request(self, request):
        """Processa requisição e carrega sessão específica da aba"""
        try:
            # Extrai tabId do header ou query param
            tab_id = request.headers.get('X-Tab-Id') or request.GET.get('tab_id')
            
            if not tab_id:
                # Se não houver tabId, gera um novo
                tab_id = str(uuid.uuid4())
                # Marca para que o cliente receba o tabId na resposta
                request._new_tab_id = tab_id
            
            request.tab_id = tab_id
            
            # Procura sessão existente desta aba
            try:
                tab_session = TabSession.objects.select_related('user').get(
                    tab_id=tab_id,
                    is_active=True
                )
                
                # Verifica se expirou
                if tab_session.is_expired():
                    tab_session.deactivate()
                    request.tab_session = None
                    request.user = AnonymousUser()
                    return None
                
                # Atualiza last_activity
                tab_session.extend_expiration()
                request.tab_session = tab_session
                
                # Se há usuário associado, o usa
                if tab_session.user and tab_session.user.is_active:
                    # Cria um objeto usuário modificado com a role snapshot
                    request.user = tab_session.user
                    # Armazena a role_snapshot no request para uso posterior
                    request.tab_role = tab_session.role_snapshot
                
            except TabSession.DoesNotExist:
                # Primeira vez que vê este tabId
                request.tab_session = None
                
        except Exception as e:
            # Se algo der errado, não quebra a aplicação
            print(f"Erro no TabSessionMiddleware: {e}")
            import traceback
            traceback.print_exc()
            request.tab_id = str(uuid.uuid4())
            request.tab_session = None
        
        return None
    
    def process_response(self, request, response):
        """Adiciona header com tabId para o cliente"""
        try:
            if hasattr(request, '_new_tab_id'):
                # Envia novo tabId para o cliente registrar
                response['X-New-Tab-Id'] = request._new_tab_id
            
            if hasattr(request, 'tab_id'):
                # Confirma o tabId sendo usado
                response['X-Tab-Id'] = request.tab_id
                
        except Exception as e:
            print(f"Erro ao adicionar headers no TabSessionMiddleware: {e}")
        
        return response


class TabRolePreservationMiddleware(MiddlewareMixin):
    """
    Middleware que preserva o role/perfil específico da aba.
    
    Garante que request.user.profile.role sempre retorna o valor 
    correto para a aba específica, não o do banco de dados.
    """
    
    def process_request(self, request):
        """Preserva o role específico da aba"""
        try:
            if hasattr(request, 'tab_session') and request.tab_session:
                if request.tab_session.role_snapshot:
                    # Modifica temporariamente o profile para retornar o role snapshot
                    if hasattr(request.user, 'profile'):
                        # Armazena o role original
                        if not hasattr(request.user, '_original_profile'):
                            original_profile = request.user.profile
                            request.user._original_profile = original_profile
                            
                            # Cria um proxy do profile com role sobrescrito
                            class ProfileProxy:
                                def __init__(self, original, role_override):
                                    self._original = original
                                    self._role_override = role_override
                                
                                @property
                                def role(self):
                                    return self._role_override
                                
                                def get_role_display(self):
                                    choices = {
                                        'admin': 'Administrador',
                                        'gestor': 'Gestor do Prédio',
                                        'lider': 'Líder de Equipe',
                                        'colaborador': 'Colaborador',
                                    }
                                    return choices.get(self._role_override, self._role_override)
                                
                                def __getattr__(self, name):
                                    return getattr(self._original, name)
                            
                            request.user.profile = ProfileProxy(
                                original_profile, 
                                request.tab_session.role_snapshot
                            )
        except Exception as e:
            print(f"Erro no TabRolePreservationMiddleware: {e}")
        
        return None
