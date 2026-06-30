# Generated migration for TabSession models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0005_remove_userprofile_email_code_expires_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TabSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tab_id', models.CharField(db_index=True, default=uuid.uuid4, max_length=36, unique=True)),
                ('session_key', models.CharField(blank=True, db_index=True, max_length=40, null=True)),
                ('role_snapshot', models.CharField(blank=True, choices=[('admin', 'Administrador'), ('gestor', 'Gestor do Prédio'), ('lider', 'Líder de Equipe'), ('colaborador', 'Colaborador')], max_length=20, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('user_agent', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_activity', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField(db_index=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tab_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Sessão de Aba',
                'verbose_name_plural': 'Sessões de Abas',
                'db_table': 'tab_session',
            },
        ),
        migrations.CreateModel(
            name='TabSessionLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=50)),
                ('details', models.JSONField(blank=True, default=dict)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tab_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='users.tabsession')),
            ],
            options={
                'verbose_name': 'Log de Sessão de Aba',
                'verbose_name_plural': 'Logs de Sessões de Abas',
                'db_table': 'tab_session_log',
            },
        ),
        migrations.AddIndex(
            model_name='tabsession',
            index=models.Index(fields=['tab_id', 'is_active'], name='tab_session_tab_id_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='tabsession',
            index=models.Index(fields=['user', 'is_active'], name='tab_session_user_is_active_idx'),
        ),
        migrations.AddIndex(
            model_name='tabsession',
            index=models.Index(fields=['expires_at'], name='tab_session_expires_at_idx'),
        ),
        migrations.AddIndex(
            model_name='tabsessionlog',
            index=models.Index(fields=['tab_session', 'created_at'], name='tab_session_log_tab_session_created_at_idx'),
        ),
    ]
