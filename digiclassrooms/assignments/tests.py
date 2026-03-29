from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from classrooms.models import Classroom
from .models import Assignment, Question, Choice, Submission, SubmissionDraft


class AssignmentPolicyTests(TestCase):
	def setUp(self):
		self.teacher = User.objects.create_user(username='teacher_a', password='pass12345')
		self.teacher.profile.is_teacher = True
		self.teacher.profile.save()

		self.student = User.objects.create_user(username='student_a', password='pass12345')

		self.classroom = Classroom.objects.create(name='Science', description='Sci', teacher=self.teacher)

		self.assignment = Assignment.objects.create(
			classroom=self.classroom,
			title='Quiz 1',
			due_date=timezone.now() + timedelta(hours=1),
			max_attempts=2,
			late_submission_policy=Assignment.LATE_POLICY_DENY,
		)
		self.question = Question.objects.create(assignment=self.assignment, text='2 + 2 = ?')
		self.correct = Choice.objects.create(question=self.question, text='4', is_correct=True)
		self.wrong = Choice.objects.create(question=self.question, text='5', is_correct=False)

	def test_save_draft_creates_or_updates_draft(self):
		self.client.login(username='student_a', password='pass12345')
		url = reverse('take_assignment', kwargs={'pk': self.assignment.pk})

		resp = self.client.post(url, data={'action': 'save_draft', f'question_{self.question.id}': self.correct.id})
		self.assertEqual(resp.status_code, 302)
		draft = SubmissionDraft.objects.get(assignment=self.assignment, student=self.student)
		self.assertEqual(str(draft.answers[str(self.question.id)]), str(self.correct.id))

	def test_late_policy_deny_blocks_submission(self):
		self.assignment.due_date = timezone.now() - timedelta(minutes=1)
		self.assignment.late_submission_policy = Assignment.LATE_POLICY_DENY
		self.assignment.save(update_fields=['due_date', 'late_submission_policy'])

		self.client.login(username='student_a', password='pass12345')
		url = reverse('take_assignment', kwargs={'pk': self.assignment.pk})
		resp = self.client.post(url, data={'action': 'submit', f'question_{self.question.id}': self.correct.id})

		self.assertEqual(resp.status_code, 302)
		self.assertFalse(Submission.objects.filter(assignment=self.assignment, student=self.student).exists())

	def test_max_attempts_prevents_third_submission(self):
		self.client.login(username='student_a', password='pass12345')
		url = reverse('take_assignment', kwargs={'pk': self.assignment.pk})

		self.client.post(url, data={'action': 'submit', f'question_{self.question.id}': self.correct.id})
		self.client.post(url, data={'action': 'submit', f'question_{self.question.id}': self.correct.id})
		self.client.post(url, data={'action': 'submit', f'question_{self.question.id}': self.correct.id})

		self.assertEqual(Submission.objects.filter(assignment=self.assignment, student=self.student).count(), 2)

	def test_late_penalty_applies(self):
		self.assignment.due_date = timezone.now() - timedelta(minutes=1)
		self.assignment.late_submission_policy = Assignment.LATE_POLICY_PENALTY
		self.assignment.late_penalty_percent = 50
		self.assignment.save(update_fields=['due_date', 'late_submission_policy', 'late_penalty_percent'])

		self.client.login(username='student_a', password='pass12345')
		url = reverse('take_assignment', kwargs={'pk': self.assignment.pk})
		self.client.post(url, data={'action': 'submit', f'question_{self.question.id}': self.correct.id})

		submission = Submission.objects.get(assignment=self.assignment, student=self.student)
		self.assertTrue(submission.is_late)
		self.assertEqual(submission.late_penalty_percent, 50)
		self.assertEqual(submission.score, 0)
