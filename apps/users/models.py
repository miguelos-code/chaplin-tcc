from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import os

class Especialidade(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = "Especialidade"
        verbose_name_plural = "Especialidades"

class ActivityLog(models.Model):
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_logs')
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='target_logs')
    action = models.CharField(max_length=255)
    role_old = models.CharField(max_length=50, blank=True, null=True)
    role_new = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.admin_user} -> {self.action} on {self.target_user} at {self.timestamp}"

    class Meta:
        verbose_name = "Log de Atividade"
        verbose_name_plural = "Logs de Atividades"

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('gestor', 'Gestor do Prédio'),
        ('lider', 'Líder de Equipe'),
        ('colaborador', 'Colaborador'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='colaborador')
    especialidade = models.ForeignKey(Especialidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='profissionais')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True)
    cpf = models.CharField(max_length=14, blank=True, verbose_name="CPF")
    cnpj = models.CharField(max_length=18, blank=True, verbose_name="CNPJ")
    bio = models.TextField(blank=True)
    cep = models.CharField(max_length=9, blank=True)
    logradouro = models.CharField(max_length=255, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"
    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = 'admin' if instance.is_superuser else 'colaborador'
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role})
    else:
        profile, _ = UserProfile.objects.get_or_create(user=instance)
        profile.save()

@receiver(post_save, sender=UserProfile)
def sync_user_role(sender, instance, **kwargs):
    user = instance.user
    changed = False
    is_admin = (instance.role == 'admin')
    if user.is_superuser != is_admin:
        user.is_superuser = is_admin
        changed = True
    if user.is_staff != is_admin:
        user.is_staff = is_admin
        changed = True
    if changed:
        user.save(update_fields=['is_superuser', 'is_staff'])

@receiver(post_delete, sender=UserProfile)
def auto_delete_avatar_on_delete(sender, instance, **kwargs):
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)
