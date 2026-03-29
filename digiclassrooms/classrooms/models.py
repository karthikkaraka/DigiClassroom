import uuid
from django.db import models
from django.contrib.auth.models import User
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager
    from notices.models import Notice
    from lectures.models import Lecture
    from assignments.models import Assignment

class Classroom(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teaching_classroom')
    students = models.ManyToManyField(User, related_name='enrolled_classrooms', blank=True)
    description = models.TextField(blank=True)
    join_key = models.CharField(max_length=8, unique=True, default='', editable=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    
    if TYPE_CHECKING:
        id: int
        pk: int
        notices: 'RelatedManager[Notice]'
        lectures: 'RelatedManager[Lecture]'
        assignments: 'RelatedManager[Assignment]'

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.join_key:
            self.join_key = self.generate_join_key()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_join_key():
        """Generate a unique 8-character join key for the classroom"""
        return str(uuid.uuid4())[:8].upper()
    
    def regenerate_join_key(self):
        """Regenerate a new join key for this classroom"""
        self.join_key = self.generate_join_key()
        self.save()
