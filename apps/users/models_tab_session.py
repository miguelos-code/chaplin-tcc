"""
Modelo para armazenar sessões isoladas por aba do navegador.
Permite múltiplos usuários com diferentes roles em abas diferentes.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class TabSession(models.Model):
    """
    Armazena informações de sessão isoladas por aba do navegador.
    Cada aba tem seu próprio tabId único e pode ter uma sessão diferente.
    """
    tab_id = models.CharField(max_length=36, unique=True, db_index=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tab_sessions', null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True, null=True, db_index=True)
    
    # Armazena a role/perfil específico desta aba
    role_snapshot = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        choices=[
            ('admin', 'Administrador'),
            ('gestor', 'Gestor do Prédio'),
            ('lider', 'Líder de Equipe'),
            ('colaborador', 'Colaborador'),
        ]
    )
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(db_index=True)
    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'tab_session'
        indexes = [
            models.Index(fields=['tab_id', 'is_active']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
        verbose_name = "Sessão de Aba"
        verbose_name_plural = "Sessões de Abas"
    
    def __str__(self):
        user_display = f"{self.user.username}" if self.user else "Anônimo"
        role_display = f" ({self.get_role_snapshot_display()})" if self.role_snapshot else ""
        return f"{user_display}{role_display} - {self.tab_id[:8]}"
    
    def is_expired(self):
        """Verifica se a sessão expirou"""
        return timezone.now() > self.expires_at or not self.is_active
    
    def extend_expiration(self, days=14):
        """Estende a expiração da sessão"""
        self.expires_at = timezone.now() + timezone.timedelta(days=days)
        self.save(update_fields=['expires_at', 'last_activity'])
    
    def deactivate(self):
        """Deactiva a sessão"""
        self.is_active = False
        self.save(update_fields=['is_active'])


class TabSessionLog(models.Model):
    """Log de atividades nas sessões de abas"""
    tab_session = models.ForeignKey(TabSession, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=50)  # login, logout, role_change, etc
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tab_session_log'
        indexes = [
            models.Index(fields=['tab_session', 'created_at']),
        ]
        verbose_name = "Log de Sessão de Aba"
        verbose_name_plural = "Logs de Sessões de Abas"
    
    def __str__(self):
        return f"{self.tab_session} - {self.action} at {self.created_at}"
