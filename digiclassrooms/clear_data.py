import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'digiclassrooms.settings')
django.setup()

from django.contrib.auth.models import User
from classrooms.models import Classroom
from lectures.models import Lecture, LectureComment
from notices.models import Notice, NoticeComment
from assignments.models import Assignment, Question, Choice, Submission, StudentAnswer
from users.models import Profile

# Delete all related objects
LectureComment.objects.all().delete()
Lecture.objects.all().delete()
NoticeComment.objects.all().delete()
Notice.objects.all().delete()
StudentAnswer.objects.all().delete()
Submission.objects.all().delete()
Choice.objects.all().delete()
Question.objects.all().delete()
Assignment.objects.all().delete()
Classroom.objects.all().delete()

print("All data cleared.")
