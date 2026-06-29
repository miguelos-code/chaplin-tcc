from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, ActivityLog, Especialidade
from .forms import UserRegistrationForm, AdminUserCreateForm
from django.db.models import Q
from django.core.paginator import Paginator
from apps.tasks.views import _is_manager
from django.utils.html import strip_tags

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tasks:dashboard')
        else:
            return render(request, 'users/login.html', {'error': 'Usuário ou senha inválidos. Tente novamente.'})
    return render(request, 'users/login.html')





from django.views.decorators.http import require_POST

@require_POST
def logout_view(request):
    logout(request)
    return redirect('core:index')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')
            user.set_password(password)
            user.is_active = True 
            user.save()
            profile = user.profile
            profile.role = form.cleaned_data.get('role', 'gestor')
            profile.cpf = form.cleaned_data.get('cpf', '')
            profile.cnpj = form.cleaned_data.get('cnpj', '')
            profile.save()
            messages.success(request, 'Conta criada com sucesso! Você já pode entrar na plataforma.')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile_view(request):
    profile = request.user.profile
    return render(request, 'users/profile.html', {'profile': profile})

def is_admin(user):
    return user.is_superuser or (hasattr(user, 'profile') and user.profile.role == 'admin')

@login_required
@user_passes_test(is_admin)
def admin_users_list_view(request):
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    users_list = User.objects.filter(is_superuser=False).order_by('-date_joined')
    if query:
        users_list = users_list.filter(
            Q(username__icontains=query) | 
            Q(email__icontains=query) |
            Q(first_name__icontains=query)
        )
    if role_filter:
        users_list = users_list.filter(profile__role=role_filter)
    paginator = Paginator(users_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'query': query,
        'role_filter': role_filter,
        'roles': UserProfile.ROLE_CHOICES
    }
    return render(request, 'users/admin/list.html', context)

@login_required
@user_passes_test(is_admin)
def admin_user_create_view(request):
    especialidades = Especialidade.objects.all()

    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = strip_tags(user.first_name)
            user.last_name = strip_tags(user.last_name)
            user.email = strip_tags(user.email)
            user.username = strip_tags(user.username)
            user.set_password(form.cleaned_data['password'])
            user.is_active = True
            user.save()

            profile = user.profile
            profile.role = form.cleaned_data.get('role', 'colaborador')
            profile.phone = form.cleaned_data.get('phone', '')
            profile.cpf = form.cleaned_data.get('cpf', '')
            profile.cnpj = form.cleaned_data.get('cnpj', '')

            esp_id = request.POST.get('especialidade')
            if esp_id:
                profile.especialidade_id = esp_id

            profile.save()

            ActivityLog.objects.create(
                admin_user=request.user,
                target_user=user,
                action='CREATE_USER',
                role_old='',
                role_new=profile.role,
                ip_address=request.META.get('REMOTE_ADDR')
            )

            messages.success(request, f'Usuário "{user.username}" criado com sucesso como {profile.get_role_display()}.')
            return redirect('users:admin_users_list')
    else:
        form = AdminUserCreateForm()

    return render(request, 'users/admin/create.html', {
        'form': form,
        'especialidades': especialidades,
    })


@login_required
@user_passes_test(is_admin)
def admin_user_edit_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user.is_superuser:
        messages.error(request, 'Não é possível editar a conta de um Administrador Mestre.')
        return redirect('users:admin_users_list')
    especialidades = Especialidade.objects.all()
    if request.method == 'POST':
        target_user.first_name = strip_tags(request.POST.get('first_name', target_user.first_name))
        target_user.last_name = strip_tags(request.POST.get('last_name', target_user.last_name))
        target_user.email = strip_tags(request.POST.get('email', target_user.email))
        target_user.profile.phone = request.POST.get('phone', target_user.profile.phone)
        target_user.profile.cpf = request.POST.get('cpf', target_user.profile.cpf)
        target_user.profile.cnpj = request.POST.get('cnpj', target_user.profile.cnpj)
        new_role = request.POST.get('role')
        old_role = target_user.profile.role
        if new_role and new_role != old_role:
            target_user.profile.role = new_role
            if new_role == 'admin':
                target_user.is_superuser = True
                target_user.is_staff = True
            else:
                target_user.is_superuser = False
            ActivityLog.objects.create(
                admin_user=request.user,
                target_user=target_user,
                action='CHANGE_ROLE',
                role_old=old_role,
                role_new=new_role,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f"Nível de conta alterado de {old_role} para {new_role}.")
        esp_id = request.POST.get('especialidade')
        if esp_id:
            target_user.profile.especialidade_id = esp_id
        target_user.save()
        target_user.profile.save()
        messages.success(request, "Usuário atualizado com sucesso.")
        return redirect('users:admin_users_list')
    return render(request, 'users/admin/edit.html', {
        'target_user': target_user,
        'roles': UserProfile.ROLE_CHOICES,
        'especialidades': especialidades
    })

@login_required
@user_passes_test(is_admin)
def admin_user_delete_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    if target_user == request.user:
        messages.error(request, 'Você não pode excluir sua própria conta.')
        return redirect('users:admin_users_list')
    if target_user.is_superuser:
        messages.error(request, 'Não é possível excluir a conta de um Administrador Mestre.')
        return redirect('users:admin_users_list')
    if request.method == 'POST':
        action = request.POST.get('action', 'deactivate')
        username = target_user.username
        if action == 'delete':
            ActivityLog.objects.create(
                admin_user=request.user,
                target_user=None,
                action='DELETE_USER',
                role_old=target_user.profile.role if hasattr(target_user, 'profile') else '',
                role_new='',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            target_user.delete()
            messages.success(request, f'Usuário "{username}" excluído permanentemente.')
        else:
            target_user.is_active = False
            target_user.save()
            ActivityLog.objects.create(
                admin_user=request.user,
                target_user=target_user,
                action='DEACTIVATE_USER',
                role_old=target_user.profile.role if hasattr(target_user, 'profile') else '',
                role_new='',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request, f'Usuário "{username}" desativado com sucesso.')
        return redirect('users:admin_users_list')
    return render(request, 'users/admin/delete.html', {
        'target_user': target_user,
    })
