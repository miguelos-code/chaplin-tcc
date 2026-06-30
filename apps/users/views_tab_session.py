"""
Views para gerenciar sessões de abas (isolamento de roles em múltiplas abas).
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
from apps.users.models_tab_session import TabSession
from apps.users.tab_session_utils import (
    create_tab_session, get_tab_session, invalidate_tab_session,
    change_tab_role, get_user_active_tabs
)


@ensure_csrf_cookie
@require_http_methods(["GET"])
def register_tab(request):
    """
    Registra uma nova aba e retorna um tabId único.
    
    GET /api/tabs/register/
    Returns: { tab_id, is_new }
    """
    tab_id = request.GET.get('tab_id')
    
    # Se já tem tabId, verifica se ainda é válido
    if tab_id:
        tab_session = get_tab_session(tab_id)
        if tab_session:
            return JsonResponse({
                'tab_id': tab_id,
                'is_new': False,
                'user': tab_session.user.username if tab_session.user else None,
                'role': tab_session.role_snapshot,
            })
    
    # Cria nova sessão de aba
    tab_session = create_tab_session(
        user=request.user if request.user.is_authenticated else None,
        role=request.user.profile.role if request.user.is_authenticated and hasattr(request.user, 'profile') else None,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )
    
    return JsonResponse({
        'tab_id': tab_session.tab_id,
        'is_new': True,
        'user': tab_session.user.username if tab_session.user else None,
        'role': tab_session.role_snapshot,
    })


@require_POST
@csrf_exempt  # Por enquanto, sem CSRF para facilitar testes
def tab_login(request):
    """
    Faz login em uma aba específica.
    
    POST /api/tabs/login/
    Body: { tab_id, username, password }
    Returns: { success, tab_id, user, role, error }
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    
    tab_id = data.get('tab_id')
    username = data.get('username')
    password = data.get('password')
    
    if not all([tab_id, username, password]):
        return JsonResponse({'success': False, 'error': 'Parâmetros faltando'}, status=400)
    
    # Autentica o usuário
    user = authenticate(request, username=username, password=password)
    
    if user is None:
        return JsonResponse({'success': False, 'error': 'Usuário ou senha inválidos'}, status=401)
    
    # Determina o role do usuário
    role = 'admin' if user.is_superuser else (user.profile.role if hasattr(user, 'profile') else 'colaborador')
    
    # Cria/atualiza sessão de aba
    tab_session = create_tab_session(
        tab_id=tab_id,
        user=user,
        role=role,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
    )
    
    return JsonResponse({
        'success': True,
        'tab_id': tab_session.tab_id,
        'user': user.username,
        'role': role,
        'message': 'Login realizado com sucesso'
    })


@require_POST
@csrf_exempt
def tab_logout(request):
    """
    Faz logout de uma aba específica.
    
    POST /api/tabs/logout/
    Body: { tab_id }
    Returns: { success }
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    
    tab_id = data.get('tab_id')
    
    if not tab_id:
        return JsonResponse({'success': False, 'error': 'tab_id faltando'}, status=400)
    
    success = invalidate_tab_session(tab_id)
    
    return JsonResponse({
        'success': success,
        'message': 'Logout realizado' if success else 'Sessão não encontrada'
    })


@login_required
@require_http_methods(["GET"])
def tab_status(request):
    """
    Retorna o status da sessão atual da aba.
    
    GET /api/tabs/status/
    Returns: { tab_id, user, role, expires_at }
    """
    if hasattr(request, 'tab_session') and request.tab_session:
        tab_session = request.tab_session
        return JsonResponse({
            'tab_id': tab_session.tab_id,
            'user': tab_session.user.username if tab_session.user else None,
            'role': tab_session.role_snapshot,
            'expires_at': tab_session.expires_at.isoformat(),
            'is_authenticated': True,
        })
    
    return JsonResponse({
        'is_authenticated': False,
        'error': 'Nenhuma sessão de aba ativa'
    }, status=401)


@login_required
@require_http_methods(["GET"])
def tab_list_active(request):
    """
    Lista todas as abas ativas do usuário.
    
    GET /api/tabs/active/
    Returns: { tabs: [...] }
    """
    tabs = get_user_active_tabs(request.user)
    
    return JsonResponse({
        'tabs': [
            {
                'tab_id': tab.tab_id[:8],  # Apenas os primeiros 8 caracteres
                'role': tab.role_snapshot,
                'created_at': tab.created_at.isoformat(),
                'last_activity': tab.last_activity.isoformat(),
                'is_current': tab.tab_id == getattr(request, 'tab_id', None),
            }
            for tab in tabs
        ]
    })


@require_POST
@csrf_exempt
def tab_change_role(request):
    """
    Muda o role de uma aba específica (apenas para admin).
    
    POST /api/tabs/change-role/
    Body: { tab_id, new_role }
    Returns: { success, role }
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'JSON inválido'}, status=400)
    
    tab_id = data.get('tab_id')
    new_role = data.get('new_role')
    
    if not all([tab_id, new_role]):
        return JsonResponse({'success': False, 'error': 'Parâmetros faltando'}, status=400)
    
    tab_session = get_tab_session(tab_id)
    if not tab_session:
        return JsonResponse({'success': False, 'error': 'Sessão não encontrada'}, status=404)
    
    # Verifica permissões (apenas admin pode fazer isso)
    if not (request.user.is_authenticated and (request.user.is_superuser or 
            (hasattr(request.user, 'profile') and request.user.profile.role == 'admin'))):
        return JsonResponse({'success': False, 'error': 'Permissão negada'}, status=403)
    
    # Muda o role
    tab_session = change_tab_role(tab_id, new_role)
    
    return JsonResponse({
        'success': True,
        'role': tab_session.role_snapshot if tab_session else None,
    })


def get_client_ip(request):
    """Extrai o IP do cliente da requisição"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
