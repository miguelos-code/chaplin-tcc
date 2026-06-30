from django.urls import path
from . import views
from . import views_tab_session

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('admin-panel/usuarios/', views.admin_users_list_view, name='admin_users_list'),
    path('admin-panel/usuarios/novo/', views.admin_user_create_view, name='admin_user_create'),
    path('admin-panel/usuarios/<int:user_id>/editar/', views.admin_user_edit_view, name='admin_user_edit'),
    path('admin-panel/usuarios/<int:user_id>/excluir/', views.admin_user_delete_view, name='admin_user_delete'),
    
    # APIs de gerenciamento de sessões por aba
    path('api/tabs/register/', views_tab_session.register_tab, name='api_tab_register'),
    path('api/tabs/login/', views_tab_session.tab_login, name='api_tab_login'),
    path('api/tabs/logout/', views_tab_session.tab_logout, name='api_tab_logout'),
    path('api/tabs/status/', views_tab_session.tab_status, name='api_tab_status'),
    path('api/tabs/active/', views_tab_session.tab_list_active, name='api_tab_list_active'),
    path('api/tabs/change-role/', views_tab_session.tab_change_role, name='api_tab_change_role'),
]
