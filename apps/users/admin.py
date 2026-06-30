from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, ActivityLog, Especialidade
from .models_tab_session import TabSession, TabSessionLog


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'company_name', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__email', 'company_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('admin_user', 'action', 'target_user', 'timestamp')
    list_filter = ('action', 'timestamp')
    search_fields = ('admin_user__username', 'target_user__username', 'action')
    readonly_fields = ('timestamp',)


@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'created_at')
    search_fields = ('nome',)
    readonly_fields = ('created_at',)


@admin.register(TabSession)
class TabSessionAdmin(admin.ModelAdmin):
    list_display = ('tab_id', 'user', 'role_snapshot', 'is_active', 'created_at', 'last_activity')
    list_filter = ('is_active', 'role_snapshot', 'created_at', 'last_activity')
    search_fields = ('tab_id', 'user__username')
    readonly_fields = ('tab_id', 'created_at', 'last_activity', 'expires_at')
    
    fieldsets = (
        ('Informações da Aba', {
            'fields': ('tab_id', 'user', 'role_snapshot')
        }),
        ('Segurança', {
            'fields': ('session_key', 'ip_address', 'user_agent', 'is_active')
        }),
        ('Datas', {
            'fields': ('created_at', 'last_activity', 'expires_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TabSessionLog)
class TabSessionLogAdmin(admin.ModelAdmin):
    list_display = ('tab_session', 'action', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('tab_session__tab_id', 'action')
    readonly_fields = ('created_at', 'details')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil de Usuário'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
