"""
Context processors para adicionar dados ao contexto de todos os templates
"""
from apps.users.tab_session_utils import get_request_role


def tab_session_context(request):
    """Adiciona informações de Tab Session ao contexto de template"""
    return {
        'current_role': get_request_role(request),
        'current_tab_id': getattr(request, 'tab_id', None),
    }
