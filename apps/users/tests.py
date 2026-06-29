from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileSignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='password123')

    def test_profile_created_on_user_creation(self):
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertEqual(self.user.profile.role, 'colaborador')

    def test_promotion_to_admin_grants_superuser(self):
        self.user.profile.role = 'admin'
        self.user.profile.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_superuser)
        self.assertTrue(self.user.is_staff)

    def test_demotion_from_admin_revokes_superuser(self):
        self.user.profile.role = 'admin'
        self.user.profile.save()
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_superuser)
        self.user.profile.role = 'colaborador'
        self.user.profile.save()
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_superuser)
        self.assertFalse(self.user.is_staff)
