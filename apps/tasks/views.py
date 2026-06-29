from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import Task, TaskEvidence, Message, Notification
from .forms import TaskForm
from apps.users.models import UserProfile
from django.db.models import Q
from django.contrib.auth.models import User as AuthUser
from django.contrib import messages as django_messages
from django.utils.html import strip_tags


def _notify(recipient, titulo, mensagem='', tipo='sistema', task=None):
    if recipient:
        Notification.objects.create(
            recipient=recipient,
            titulo=titulo,
            mensagem=mensagem,
            tipo=tipo,
            task=task,
        )


def _get_role(user):
    return getattr(getattr(user, 'profile', None), 'role', 'colaborador')


def _is_manager(user):
    return _get_role(user) in ('admin', 'gestor', 'lider')

@login_required
def dashboard_view(request):
    if not hasattr(request.user, 'profile'):
        UserProfile.objects.create(user=request.user, role='admin' if request.user.is_superuser else 'colaborador')
    user_profile = request.user.profile
    if user_profile.role == 'gestor':
        tasks = Task.objects.filter(created_by=request.user)
    elif user_profile.role == 'lider':
        tasks = Task.objects.filter(
            Q(assigned_to=request.user) | Q(assigned_leader=request.user)
        ).distinct()
    elif user_profile.role == 'colaborador':
        tasks = Task.objects.filter(assigned_to=request.user)
    else:
        tasks = Task.objects.all()
    context = {
        'tasks': tasks,
        'total_tasks': tasks.count(),
        'open_tasks': tasks.filter(status='aberta').count(),
        'assigned_tasks': tasks.filter(status='alocada').count(),
        'completed_tasks': tasks.filter(status='concluida').count(),
        'finalized_tasks': tasks.filter(status='finalizada').count(),
    }
    return render(request, 'tasks/dashboard.html', context)

@login_required
def tasks_list_view(request):
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    search = request.GET.get('search', '')
    responsavel = request.GET.get('responsavel', '')
    user_profile = getattr(request.user, 'profile', None)
    if user_profile and user_profile.role == 'gestor':
        tasks = Task.objects.filter(created_by=request.user)
    elif user_profile and user_profile.role == 'lider':
        tasks = Task.objects.filter(
            Q(assigned_to=request.user) | Q(assigned_leader=request.user)
        ).distinct()
    elif user_profile and user_profile.role == 'colaborador':
        tasks = Task.objects.filter(assigned_to=request.user)
    else:
        tasks = Task.objects.all()
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )
    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)
    if responsavel:
        tasks = tasks.filter(assigned_to__username=responsavel) 
    context = {
        'tasks': tasks,
        'current_status': status,
        'current_priority': priority,
        'current_search': search,
        'can_manage': _is_manager(request.user),
    }
    if request.GET.get('ajax') == '1':
        return render(request, 'tasks/_list_table.html', context)
    return render(request, 'tasks/list.html', context)

@login_required
def create_task_view(request):
    if not _is_manager(request.user):
        django_messages.error(request, 'Você não tem permissão para criar tarefas.')
        return redirect('tasks:list')
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            
            photo = form.cleaned_data.get('photo')
            if photo:
                TaskEvidence.objects.create(task=task, photo=photo, description='Foto adicionada na abertura da tarefa.')
                
            for user in AuthUser.objects.filter(profile__role__in=['gestor', 'admin']).exclude(pk=request.user.pk):
                _notify(user, f'Nova tarefa criada: {task.title}',
                        mensagem=f'Criada por {request.user.get_full_name() or request.user.username}.',
                        tipo='tarefa_criada', task=task)
            return redirect('tasks:detail', pk=task.pk)
    else:
        form = TaskForm()

    return render(request, 'tasks/create.html', {'form': form})

@login_required
def task_detail_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    role = _get_role(request.user)
    # Controle de acesso por perfil
    if role == 'colaborador' and task.assigned_to_id != request.user.id:
        django_messages.error(request, 'Você não tem acesso a esta tarefa.')
        return redirect('tasks:list')
    elif role == 'gestor' and task.created_by_id != request.user.id:
        django_messages.error(request, 'Você não tem acesso a esta tarefa.')
        return redirect('tasks:list')
    elif role == 'lider' and task.assigned_to_id != request.user.id and task.assigned_leader_id != request.user.id:
        django_messages.error(request, 'Você não tem acesso a esta tarefa.')
        return redirect('tasks:list')
    task_messages = task.messages.all()
    evidences = task.evidences.all()

    return render(request, 'tasks/detail.html', {
        'task': task,
        'task_messages': task_messages,
        'evidences': evidences,
        'can_manage': _is_manager(request.user),
    })

@login_required
def edit_task_view(request, pk):
    if not _is_manager(request.user):
        django_messages.error(request, 'Você não tem permissão para editar tarefas.')
        return redirect('tasks:detail', pk=pk)
    task = get_object_or_404(Task, pk=pk)
    if task.status == 'finalizada':
        django_messages.error(request, 'Tarefas finalizadas não podem ser editadas.')
        return redirect('tasks:detail', pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            saved_task = form.save()
            photo = request.FILES.get('photo')
            if photo:
                evidence = saved_task.evidences.first()
                if evidence:
                    evidence.photo = photo
                    evidence.save()
                else:
                    TaskEvidence.objects.create(task=saved_task, photo=photo, description='Foto adicionada via edição.')
            return redirect('tasks:detail', pk=task.pk)
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/edit.html', {'form': form, 'task': task})

@login_required
def assign_task_view(request, pk):
    if not _is_manager(request.user):
        django_messages.error(request, 'Você não tem permissão para alocar tarefas.')
        return redirect('tasks:detail', pk=pk)
    
    task = get_object_or_404(Task, pk=pk)

    if task.status in ('concluida', 'finalizada'):
        django_messages.error(request, 'Não é possível alocar tarefas concluídas ou finalizadas.')
        return redirect('tasks:detail', pk=pk)
    
    current_role = _get_role(request.user)
    if current_role == 'gestor':
        # Gestor pode alocar para Líderes ou Colaboradores
        users = AuthUser.objects.filter(is_active=True, profile__role__in=['lider', 'colaborador']).order_by('first_name', 'username')
    elif current_role == 'lider':
        users = AuthUser.objects.filter(is_active=True, profile__role='colaborador').order_by('first_name', 'username')
    else:
        users = AuthUser.objects.filter(is_active=True).exclude(profile__role='admin').order_by('first_name', 'username')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if not users.filter(id=user_id).exists():
            django_messages.error(request, 'Você não tem permissão para alocar a tarefa para este usuário.')
            return redirect('tasks:assign', pk=pk)
        
        target_user = AuthUser.objects.get(id=user_id)
        target_role = _get_role(target_user)

        # Se o Líder está re-alocando para um Colaborador, salvar o Líder como assigned_leader
        if current_role == 'lider' and target_role == 'colaborador':
            task.assigned_leader = request.user
        # Se o Gestor aloca diretamente para um Colaborador, não há líder intermediário
        elif current_role == 'gestor' and target_role == 'colaborador':
            task.assigned_leader = None
        # Se o Gestor aloca para um Líder, o líder fica em assigned_to (e depois ele re-aloca)
        elif current_role == 'gestor' and target_role == 'lider':
            task.assigned_leader = None
            
        task.assigned_to_id = user_id
        task.status = 'alocada'
        task.save()
        if task.assigned_to:
            _notify(task.assigned_to,
                    f'Tarefa atribuída: {task.title}',
                    mensagem=f'Você foi alocado para esta tarefa por {request.user.get_full_name() or request.user.username}.',
                    tipo='tarefa_atribuida', task=task)
        return redirect('tasks:detail', pk=task.pk)
        
    return render(request, 'tasks/assign.html', {'task': task, 'users': users})

@login_required
def complete_task_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if not _is_manager(request.user) and task.assigned_to_id != request.user.id:
        django_messages.error(request, 'Você não tem permissão para concluir esta tarefa.')
        return redirect('tasks:list')
    if task.status in ('concluida', 'finalizada'):
        django_messages.error(request, 'Esta tarefa já foi concluída.')
        return redirect('tasks:detail', pk=pk)
    if task.status == 'aberta':
        django_messages.error(request, 'A tarefa precisa estar alocada antes de ser concluída.')
        return redirect('tasks:detail', pk=pk)
    if request.method == 'POST':
        description = request.POST.get('description', '')
        photo = request.FILES.get('photo')
        if not photo:
            django_messages.error(request, 'É obrigatório enviar uma foto de evidência para concluir a tarefa.')
            return redirect('tasks:complete', pk=pk)
        evidence = TaskEvidence(
            task=task,
            description=description
        )
        if photo:
            evidence.photo = photo
        evidence.save()
        task.status = 'concluida'
        task.completed_at = timezone.now()
        task.save()
        # Notificar o Gestor (criador da tarefa)
        if task.created_by and task.created_by_id != request.user.id:
            _notify(task.created_by,
                    f'Tarefa concluída: {task.title}',
                    mensagem=f'Concluída por {request.user.get_full_name() or request.user.username}.',
                    tipo='tarefa_concluida', task=task)
        # Notificar o Líder intermediário (se existir)
        if task.assigned_leader and task.assigned_leader_id != request.user.id:
            _notify(task.assigned_leader,
                    f'Tarefa concluída: {task.title}',
                    mensagem=f'Concluída por {request.user.get_full_name() or request.user.username}.',
                    tipo='tarefa_concluida', task=task)
        return redirect('tasks:detail', pk=task.pk)
    return render(request, 'tasks/complete.html', {'task': task})

@login_required
def add_message_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(task=task, sender=request.user, content=content)
            recipients = set()
            if task.assigned_to and task.assigned_to_id != request.user.id:
                recipients.add(task.assigned_to)
            if task.created_by and task.created_by_id != request.user.id:
                recipients.add(task.created_by)
            # Incluir o Líder intermediário nas notificações de mensagem
            if task.assigned_leader and task.assigned_leader_id != request.user.id:
                recipients.add(task.assigned_leader)
            for recipient in recipients:
                _notify(recipient,
                        f'Nova mensagem em: {task.title}',
                        mensagem=f'{request.user.get_full_name() or request.user.username}: {content[:80]}',
                        tipo='nova_mensagem', task=task)
        return redirect('tasks:detail', pk=task.pk)
    return redirect('tasks:detail', pk=task.pk)


@login_required
def delete_task_view(request, pk):
    if not _is_manager(request.user):
        django_messages.error(request, 'Você não tem permissão para excluir tarefas.')
        return redirect('tasks:list')
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        titulo = task.title
        task.delete()
        django_messages.success(request, f'Tarefa "{titulo}" excluída com sucesso.')
        return redirect('tasks:list')
    return render(request, 'tasks/delete_confirm.html', {'task': task})


@login_required
def finalize_task_view(request, pk):
    if not _is_manager(request.user):
        django_messages.error(request, 'Você não tem permissão para finalizar tarefas.')
        return redirect('tasks:detail', pk=pk)
    task = get_object_or_404(Task, pk=pk)
    if task.status != 'concluida':
        django_messages.error(request, 'Apenas tarefas com status "Concluída" podem ser finalizadas.')
        return redirect('tasks:detail', pk=pk)
    if request.method == 'POST':
        task.status = 'finalizada'
        task.save()
        # Notificar o Colaborador (executor)
        if task.assigned_to and task.assigned_to_id != request.user.id:
            _notify(task.assigned_to,
                    f'Tarefa finalizada: {task.title}',
                    mensagem=f'Aprovada por {request.user.get_full_name() or request.user.username}.',
                    tipo='tarefa_finalizada', task=task)
        # Notificar o Líder intermediário (se existir)
        if task.assigned_leader and task.assigned_leader_id != request.user.id:
            _notify(task.assigned_leader,
                    f'Tarefa finalizada: {task.title}',
                    mensagem=f'Aprovada por {request.user.get_full_name() or request.user.username}.',
                    tipo='tarefa_finalizada', task=task)
        # Notificar o Gestor (criador) se não for ele mesmo finalizando
        if task.created_by and task.created_by_id != request.user.id:
            _notify(task.created_by,
                    f'Tarefa finalizada: {task.title}',
                    mensagem=f'Aprovada por {request.user.get_full_name() or request.user.username}.',
                    tipo='tarefa_finalizada', task=task)
        django_messages.success(request, f'Tarefa "{task.title}" finalizada com sucesso.')
        return redirect('tasks:detail', pk=pk)
    django_messages.error(request, 'Método não permitido.')
    return redirect('tasks:detail', pk=pk)


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(recipient=request.user)
    notifications.filter(lida=False).update(lida=True)
    return render(request, 'tasks/notifications.html', {'notifications': notifications})


from django.views.decorators.http import require_POST

@login_required
@require_POST
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.lida = True
    notif.save()
    return JsonResponse({'ok': True})


@login_required
def unread_notifications_count(request):
    count = Notification.objects.filter(recipient=request.user, lida=False).count()
    return JsonResponse({'count': count})


@login_required
def notifications_json_view(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:20]
    data = [{
        'id': n.id,
        'titulo': n.titulo,
        'mensagem': n.mensagem,
        'tipo': n.tipo,
        'lida': n.lida,
        'created_at': n.created_at.strftime('%d/%m/%Y %H:%M'),
    } for n in notifications]
    return JsonResponse({'notifications': data})


@login_required
def mark_all_notifications_read(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, lida=False).update(lida=True)
        return JsonResponse({'ok': True})
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def settings_view(request):
    if not hasattr(request.user, 'profile'):
        UserProfile.objects.create(user=request.user, role='admin' if request.user.is_superuser else 'colaborador')
    user_profile = request.user.profile
    if request.method == 'POST':
        user = request.user
        user.first_name = strip_tags(request.POST.get('first_name', user.first_name))
        user.last_name = strip_tags(request.POST.get('last_name', user.last_name))
        user.email = strip_tags(request.POST.get('email', user.email))
        user.save()
        user_profile.phone = strip_tags(request.POST.get('phone', user_profile.phone))
        user_profile.bio = strip_tags(request.POST.get('bio', user_profile.bio))
        user_profile.cpf = strip_tags(request.POST.get('cpf', user_profile.cpf))
        user_profile.cnpj = strip_tags(request.POST.get('cnpj', user_profile.cnpj))
        user_profile.cep = strip_tags(request.POST.get('cep', user_profile.cep))
        user_profile.logradouro = strip_tags(request.POST.get('logradouro', user_profile.logradouro))
        user_profile.numero = strip_tags(request.POST.get('numero', user_profile.numero))
        user_profile.complemento = strip_tags(request.POST.get('complemento', user_profile.complemento))
        user_profile.bairro = strip_tags(request.POST.get('bairro', user_profile.bairro))
        user_profile.cidade = strip_tags(request.POST.get('cidade', user_profile.cidade))
        user_profile.estado = strip_tags(request.POST.get('estado', user_profile.estado))
        
        avatar = request.FILES.get('avatar')
        if avatar:
            user_profile.avatar = avatar
            
        user_profile.save()
        return redirect('tasks:settings')
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'tasks/settings.html', context)


@login_required
def kanban_view(request):
    if not hasattr(request.user, 'profile'):
        UserProfile.objects.create(user=request.user, role='admin' if request.user.is_superuser else 'colaborador')
    user_profile = request.user.profile

    if user_profile.role == 'gestor':
        all_tasks = Task.objects.filter(created_by=request.user)
    elif user_profile.role == 'lider':
        all_tasks = Task.objects.filter(
            Q(assigned_to=request.user) | Q(assigned_leader=request.user)
        ).distinct()
    elif user_profile.role == 'colaborador':
        all_tasks = Task.objects.filter(assigned_to=request.user)
    else:
        all_tasks = Task.objects.all()

    context = {
        'tarefas_abertas': all_tasks.filter(status='aberta').select_related('assigned_to', 'created_by'),
        'tarefas_alocadas': all_tasks.filter(status='alocada').select_related('assigned_to', 'created_by'),
        'tarefas_concluidas': all_tasks.filter(status='concluida').select_related('assigned_to', 'created_by'),
        'tarefas_finalizadas': all_tasks.filter(status='finalizada').select_related('assigned_to', 'created_by'),
    }
    if request.GET.get('ajax') == '1':
        return render(request, 'tasks/_kanban_board.html', context)
    return render(request, 'tasks/kanban.html', context)



