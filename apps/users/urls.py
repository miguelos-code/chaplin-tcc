from django.urls import path
from . import views

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
]
