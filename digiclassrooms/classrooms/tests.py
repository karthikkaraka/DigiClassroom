from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Classroom


class JoinKeyTests(TestCase):
	def setUp(self):
		self.teacher = User.objects.create_user(username='teacher', password='pass12345')
		self.teacher.profile.is_teacher = True
		self.teacher.profile.save()

		self.student = User.objects.create_user(username='student', password='pass12345')

		self.classroom = Classroom.objects.create(
			name='Math',
			description='Algebra',
			teacher=self.teacher,
		)

	def test_classroom_has_expiring_join_key(self):
		self.assertTrue(self.classroom.join_key)
		self.assertIsNotNone(self.classroom.join_key_expires_at)

	def test_student_can_join_with_valid_key(self):
		self.client.login(username='student', password='pass12345')
		url = reverse('join_classroom_for_classroom', kwargs={'pk': self.classroom.pk})
		resp = self.client.post(url, data={'join_key': self.classroom.join_key})
		self.assertEqual(resp.status_code, 302)
		self.assertTrue(self.classroom.students.filter(pk=self.student.pk).exists())

	def test_student_cannot_join_with_invalid_key(self):
		self.client.login(username='student', password='pass12345')
		url = reverse('join_classroom_for_classroom', kwargs={'pk': self.classroom.pk})
		resp = self.client.post(url, data={'join_key': 'WRONGKEY'})
		self.assertEqual(resp.status_code, 302)
		self.assertFalse(self.classroom.students.filter(pk=self.student.pk).exists())

	def test_student_cannot_join_with_expired_key(self):
		self.classroom.join_key_expires_at = timezone.now() - timedelta(minutes=1)
		self.classroom.save(update_fields=['join_key_expires_at'])

		self.client.login(username='student', password='pass12345')
		url = reverse('join_classroom_for_classroom', kwargs={'pk': self.classroom.pk})
		resp = self.client.post(url, data={'join_key': self.classroom.join_key})
		self.assertEqual(resp.status_code, 302)
		self.assertFalse(self.classroom.students.filter(pk=self.student.pk).exists())

	def test_teacher_can_regenerate_join_key(self):
		old_key = self.classroom.join_key
		old_expiry = self.classroom.join_key_expires_at

		self.client.login(username='teacher', password='pass12345')
		url = reverse('regenerate_join_key', kwargs={'pk': self.classroom.pk})
		resp = self.client.post(url)
		self.assertEqual(resp.status_code, 302)

		self.classroom.refresh_from_db()
		self.assertNotEqual(self.classroom.join_key, old_key)
		self.assertGreater(self.classroom.join_key_expires_at, old_expiry)

	def test_teacher_cannot_join_as_student(self):
		self.client.login(username='teacher', password='pass12345')
		url = reverse('join_classroom_for_classroom', kwargs={'pk': self.classroom.pk})
		resp = self.client.post(url, data={'join_key': self.classroom.join_key})
		self.assertEqual(resp.status_code, 302)
		self.assertFalse(self.classroom.students.filter(pk=self.teacher.pk).exists())
