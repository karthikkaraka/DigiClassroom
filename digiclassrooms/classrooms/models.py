import secrets
import string
import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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
    join_key_expires_at = models.DateTimeField(null=True, blank=True)
    join_key_ttl_override_minutes = models.PositiveIntegerField(null=True, blank=True)
    joins_enabled = models.BooleanField(default=True)
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
            self.join_key = self.generate_unique_join_key()
        if self.join_key and not self.join_key_expires_at:
            self.join_key_expires_at = timezone.now() + timedelta(minutes=self.get_join_key_ttl_minutes())
        super().save(*args, **kwargs)
    
    @staticmethod
    def join_key_ttl_minutes() -> int:
        return int(getattr(settings, 'CLASSROOM_JOIN_KEY_TTL_MINUTES', 60))

    def get_join_key_ttl_minutes(self) -> int:
        if self.join_key_ttl_override_minutes:
            return int(self.join_key_ttl_override_minutes)
        return self.join_key_ttl_minutes()

    @classmethod
    def generate_unique_join_key(cls) -> str:
        """Generate a unique 8-character join key for the classroom."""
        alphabet = string.ascii_uppercase + string.digits
        for _ in range(100):
            candidate = ''.join(secrets.choice(alphabet) for _ in range(8))
            if not cls.objects.filter(join_key=candidate).exists():
                return candidate
        # Fallback: UUID slice (extremely unlikely to collide, but still enforce uniqueness at DB level)
        return str(uuid.uuid4())[:8].upper()

    def is_join_key_valid(self, join_key: str) -> bool:
        if not join_key:
            return False
        if join_key.strip().upper() != (self.join_key or '').upper():
            return False
        if not self.join_key_expires_at:
            return False
        return timezone.now() <= self.join_key_expires_at
    
    def regenerate_join_key(self):
        """Regenerate a new join key for this classroom"""
        self.join_key = self.generate_unique_join_key()
        self.join_key_expires_at = timezone.now() + timedelta(minutes=self.get_join_key_ttl_minutes())
        self.save(update_fields=['join_key', 'join_key_expires_at'])
