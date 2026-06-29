from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task, Notification

class TaskRBACTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser('admin', 'admin@test.com', 'pass')
        self.admin.profile.role = 'admin'
        self.admin.profile.save()
        self.gestor = User.objects.create_user('gestor', 'gestor@test.com', 'pass')
        self.gestor.profile.role = 'gestor'
        self.gestor.profile.save()

        self.colab1 = User.objects.create_user('colab1', 'c1@test.com', 'pass')
        self.colab1.profile.role = 'colaborador'
        self.colab1.profile.save()

        self.colab2 = User.objects.create_user('colab2', 'c2@test.com', 'pass')
        self.colab2.profile.role = 'colaborador'
        self.colab2.profile.save()
        self.task1 = Task.objects.create(
            title="Lâmpada Quebrada",
            description="Corredor",
            created_by=self.gestor,
            assigned_to=self.colab1,
            status='alocada'
        )
        self.task2 = Task.objects.create(
            title="Vazamento Pia",
            description="Banheiro",
            created_by=self.gestor,
            assigned_to=self.colab2,
            status='alocada'
        )

    def test_colaborador_only_sees_own_task(self):
        self.client.login(username='colab1', password='pass')
        res = self.client.get(reverse('tasks:detail', args=[self.task1.id]))
        self.assertEqual(res.status_code, 200)
        res = self.client.get(reverse('tasks:detail', args=[self.task2.id]))
        self.assertRedirects(res, reverse('tasks:list'))
    def test_gestor_can_create_and_assign(self):
        self.client.login(username='gestor', password='pass')
        res = self.client.get(reverse('tasks:create'))
        self.assertEqual(res.status_code, 200)

        res = self.client.post(reverse('tasks:create'), {
            'title': 'Nova Tarefa G',
            'description': 'Desc',
            'priority': 'normal',
        })
        self.assertEqual(res.status_code, 302) 
        new_task = Task.objects.get(title='Nova Tarefa G')
        res = self.client.post(reverse('tasks:assign', args=[new_task.id]), {
            'user_id': self.colab1.id
        })
        new_task.refresh_from_db()
        self.assertEqual(new_task.assigned_to, self.colab1)
        self.assertEqual(new_task.status, 'alocada')

    def test_colaborador_cannot_create_task(self):
        self.client.login(username='colab1', password='pass')
        res = self.client.get(reverse('tasks:create'))
        self.assertRedirects(res, reverse('tasks:list'))

        res = self.client.post(reverse('tasks:create'), {
            'title': 'Hack!', 'description': 'Hacked', 'priority': 'normal'
        })
        self.assertRedirects(res, reverse('tasks:list'))
        self.assertFalse(Task.objects.filter(title='Hack!').exists())
    def test_task_completion_lifecycle(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        photo = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

        self.client.login(username='colab1', password='pass')
        res = self.client.post(reverse('tasks:complete', args=[self.task1.id]), {
            'description': 'Feito!',
            'photo': photo
        })
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'concluida')

        self.client.login(username='gestor', password='pass')
        res = self.client.post(reverse('tasks:finalize', args=[self.task1.id]))
        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, 'finalizada')
