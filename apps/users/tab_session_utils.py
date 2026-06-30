"""
Utilitários para gerenciamento de sessões por aba.
"""
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from apps.users.models_tab_session import TabSession, TabSessionLog
import uuid


def create_tab_session(tab_id=None, user=None, role=None, ip_address=None, user_agent=None, days=14):
    """
    Cria ou atualiza uma sessão de aba.
    
    Args:
        tab_id: ID único da aba (se None, gera um novo)
        user: Usuário autenticado (pode ser None)
        role: Role/perfil específico para esta aba
        ip_address: IP do cliente
        user_agent: User-Agent do cliente
        days: Dias até expiração
    
    Returns:
        TabSession
    """
    if not tab_id:
        tab_id = str(uuid.uuid4())
    
    expires_at = timezone.now() + timedelta(days=days)
    
    tab_session, created = TabSession.objects.update_or_create(
        tab_id=tab_id,
        defaults={
            'user': user,
            'role_snapshot': role,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'expires_at': expires_at,
            'is_active': True,
        }
    )
    
    # Log da ação
    action = 'create' if created else 'update'
    TabSessionLog.objects.create(
        tab_session=tab_session,
        action=action,
        ip_address=ip_address,
        details={
            'user': user.username if user else None,
            'role': role,
        }
    )
    
    return tab_session


def get_tab_session(tab_id):
    """
    Recupera uma sessão de aba válida.
    
    Returns:
        TabSession ou None se expirada
    """
    try:
        tab_session = TabSession.objects.get(
            tab_id=tab_id,
            is_active=True
        )
        
        if tab_session.is_expired():
            tab_session.deactivate()
            return None
        
        return tab_session
    except TabSession.DoesNotExist:
        return None


def invalidate_tab_session(tab_id):
    """Invalida uma sessão de aba"""
    try:
        tab_session = TabSession.objects.get(tab_id=tab_id)
        tab_session.deactivate()
        
        TabSessionLog.objects.create(
            tab_session=tab_session,
            action='logout',
            details={}
        )
        return True
    except TabSession.DoesNotExist:
        return False


def cleanup_expired_sessions():
    """Remove sessões expiradas (deve ser chamado periodicamente)"""
    expired = TabSession.objects.filter(
        expires_at__lt=timezone.now(),
        is_active=True
    )
    count = expired.count()
    expired.update(is_active=False)
    return count


def get_user_active_tabs(user):
    """
    Retorna todas as abas ativas de um usuário.
    """
    return TabSession.objects.filter(
        user=user,
        is_active=True,
        expires_at__gt=timezone.now()
    ).order_by('-last_activity')


def change_tab_role(tab_id, new_role):
    """
    Muda o role/perfil de uma aba específica.
    
    Args:
        tab_id: ID da aba
        new_role: Novo role (admin, gestor, lider, colaborador)
    
    Returns:
        TabSession ou None
    """
    try:
        tab_session = TabSession.objects.get(tab_id=tab_id, is_active=True)
        old_role = tab_session.role_snapshot
        tab_session.role_snapshot = new_role
        tab_session.save(update_fields=['role_snapshot', 'last_activity'])
        
        TabSessionLog.objects.create(
            tab_session=tab_session,
            action='role_change',
            details={
                'old_role': old_role,
                'new_role': new_role,
            }
        )
        
        return tab_session
    except TabSession.DoesNotExist:
        return None


def logout_all_tabs(user):
    """
    Desativa todas as sessões de abas de um usuário.
    """
    tab_sessions = TabSession.objects.filter(user=user, is_active=True)
    count = tab_sessions.count()
    
    for tab_session in tab_sessions:
        tab_session.deactivate()
        TabSessionLog.objects.create(
            tab_session=tab_session,
            action='logout_all',
            details={}
        )
    
    return count
