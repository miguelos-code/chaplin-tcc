from django.contrib import admin
from .models import Task, TaskEvidence, Message

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'assigned_to', 'assigned_leader', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')

@admin.register(TaskEvidence)
class TaskEvidenceAdmin(admin.ModelAdmin):
    list_display = ('task', 'created_at')
    search_fields = ('task__title',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('task', 'sender', 'created_at')
    search_fields = ('task__title', 'sender__username')
