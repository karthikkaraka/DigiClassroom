# Implementation Guide for New Features

## Overview
This document provides step-by-step implementation instructions for the new features added to DigiClassroom.

---

## 1. Classroom Join Keys - Complete Implementation

### Step 1: Database Migration

The Classroom model has been updated with:
- `join_key` field (CharField, unique, auto-generated)
- `created_at` field (DateTimeField, auto_now_add)
- `generate_join_key()` static method
- `regenerate_join_key()` instance method

**Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Generate keys for existing classrooms:**
```bash
python manage.py generate_join_keys
```

### Step 2: Update Views

**classrooms/views.py** - Add join by key view:

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Classroom

@login_required(login_url='login')
def join_classroom_with_key(request):
    """Allow students to join classroom using join key"""
    if request.method == 'POST':
        join_key = request.POST.get('join_key', '').strip().upper()
        
        try:
            classroom = Classroom.objects.get(join_key=join_key)
            classroom.students.add(request.user)
            return redirect('classroom_detail', pk=classroom.pk)
        except Classroom.DoesNotExist:
            return render(request, 'classrooms/join_with_key.html', {
                'error': 'Invalid join key. Please check and try again.'
            })
    
    return render(request, 'classrooms/join_with_key.html')

@login_required(login_url='login')
def classroom_settings(request, pk):
    """Teacher classroom settings including join key management"""
    classroom = get_object_or_404(Classroom, pk=pk)
    if request.user != classroom.teacher:
        return redirect('home')
    
    if request.method == 'POST':
        if 'regenerate_key' in request.POST:
            classroom.regenerate_join_key()
            return redirect('classroom_settings', pk=pk)
    
    return render(request, 'classrooms/settings.html', {
        'classroom': classroom
    })
```

**classrooms/urls.py** - Add URL patterns:

```python
from django.urls import path
from . import views

urlpatterns = [
    # ... existing patterns ...
    path('join-with-key/', views.join_classroom_with_key, name='join_with_key'),
    path('<int:pk>/settings/', views.classroom_settings, name='classroom_settings'),
]
```

### Step 3: Create Templates

**classrooms/templates/classrooms/join_with_key.html:**

```html
<form method="POST">
    {% csrf_token %}
    <div class="form-group">
        <label for="join_key">Classroom Join Key (8 characters)</label>
        <input type="text" 
               name="join_key" 
               id="join_key" 
               maxlength="8" 
               placeholder="e.g., ABC12345"
               class="form-control"
               required>
    </div>
    <button type="submit" class="btn btn-primary">Join Classroom</button>
</form>
```

---

## 2. Edit and Delete Comments

### Step 1: Update Views

**lectures/views.py:**

```python
@login_required(login_url='login')
def edit_lecture_comment(request, comment_id):
    comment = get_object_or_404(LectureComment, pk=comment_id)
    
    # Check permissions
    is_author = request.user == comment.author
    is_teacher = request.user == comment.lecture.classroom.teacher
    
    if not (is_author or is_teacher):
        return redirect('lecture_detail', pk=comment.lecture.pk)
    
    if request.method == 'POST':
        form = LectureCommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.is_edited = True
            comment.save()
            return redirect('lecture_detail', pk=comment.lecture.pk)
    else:
        form = LectureCommentForm(instance=comment)
    
    return render(request, 'lectures/edit_comment.html', {
        'form': form,
        'comment': comment
    })

@login_required(login_url='login')
@require_POST
def delete_lecture_comment(request, comment_id):
    comment = get_object_or_404(LectureComment, pk=comment_id)
    lecture_id = comment.lecture.id
    
    # Check permissions
    is_author = request.user == comment.author
    is_teacher = request.user == comment.lecture.classroom.teacher
    
    if (is_author or is_teacher) and request.method == 'POST':
        comment.delete()
    
    return redirect('lecture_detail', pk=lecture_id)
```

**Similar implementation for NoticeComment in notices/views.py**

### Step 2: Add URLs

```python
# lectures/urls.py
urlpatterns = [
    # ... existing ...
    path('comment/<int:comment_id>/edit/', views.edit_lecture_comment, name='edit_lecture_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_lecture_comment, name='delete_lecture_comment'),
]
```

---

## 3. Edit and Delete Content (Lectures, Notices, Assignments)

### Step 1: Update Views

**lectures/views.py:**

```python
@login_required(login_url='login')
def edit_lecture(request, pk):
    lecture = get_object_or_404(Lecture, pk=pk)
    if request.user != lecture.classroom.teacher:
        return redirect('home')
    
    if request.method == 'POST':
        form = LectureForm(request.POST, instance=lecture)
        if form.is_valid():
            form.save()
            return redirect('lecture_detail', pk=pk)
    else:
        form = LectureForm(instance=lecture)
    
    return render(request, 'lectures/edit_lecture.html', {
        'form': form,
        'lecture': lecture
    })

@login_required(login_url='login')
@require_POST
def delete_lecture(request, pk):
    lecture = get_object_or_404(Lecture, pk=pk)
    classroom_id = lecture.classroom.id
    
    if request.user == lecture.classroom.teacher:
        lecture.delete()
    
    return redirect('lectures_list', classroom_pk=classroom_id)
```

**Similar pattern for Notice and Assignment models**

---

## 4. Search Functionality for Classes

### Step 1: Update Views

**classrooms/views.py:**

```python
from django.db.models import Q

@login_required(login_url='login')
def search_classrooms(request):
    """Search available classrooms"""
    query = request.GET.get('q', '').strip()
    classrooms = Classroom.objects.exclude(students=request.user)
    
    if query:
        classrooms = classrooms.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(teacher__first_name__icontains=query) |
            Q(teacher__last_name__icontains=query)
        )
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(classrooms, 10)  # 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'classrooms/search.html', {
        'page_obj': page_obj,
        'query': query
    })
```

**classrooms/urls.py:**

```python
urlpatterns = [
    # ... existing ...
    path('search/', views.search_classrooms, name='search_classrooms'),
]
```

---

## 5. View Past Quiz Attempts

### Step 1: Update Views

**assignments/views.py:**

```python
@login_required(login_url='login')
def submission_history(request, pk):
    """View all submission attempts for an assignment"""
    assignment = get_object_or_404(Assignment, pk=pk)
    
    if request.user != assignment.classroom.teacher:
        # Students can only see their own submissions
        submissions = Submission.objects.filter(
            assignment=assignment,
            student=request.user
        ).order_by('-submitted_at')
    else:
        # Teachers see all submissions
        submissions = assignment.submissions.all().order_by('-submitted_at')
    
    return render(request, 'assignments/submission_history.html', {
        'assignment': assignment,
        'submissions': submissions,
        'is_teacher': request.user == assignment.classroom.teacher
    })
```

**assignments/urls.py:**

```python
urlpatterns = [
    # ... existing ...
    path('submission-history/<int:pk>/', views.submission_history, name='submission_history'),
]
```

---

## 6. Assignment Due Dates Implementation

### Step 1: Update Forms

**assignments/forms.py:**

```python
from django import forms
from .models import Assignment

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                }
            )
        }
```

### Step 2: Add Status Logic

**assignments/models.py:**

```python
from django.utils import timezone

class Submission(models.Model):
    # ... existing fields ...
    
    def get_status(self):
        """Get submission status: On-time, Late, Not Submitted"""
        if not self.assignment.due_date:
            return 'No due date'
        
        if self.submitted_at > self.assignment.due_date:
            return 'Late'
        else:
            return 'On-time'
    
    def is_overdue(self):
        """Check if assignment is overdue"""
        if not self.assignment.due_date:
            return False
        return timezone.now() > self.assignment.due_date
```

---

## Testing Migration

After implementing these features:

```bash
# Generate migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Generate join keys for existing classrooms
python manage.py generate_join_keys

# Run tests (if you have them)
python manage.py test
```

---

## Frontend Template Considerations

### Comment Display with Edit/Delete
```html
{% if comment.is_edited %}
    <small class="text-muted">(edited)</small>
{% endif %}

{% if user == comment.author or user == classroom.teacher %}
    <a href="{% url 'edit_lecture_comment' comment.id %}">Edit</a>
    <form method="POST" action="{% url 'delete_lecture_comment' comment.id %}">
        {% csrf_token %}
        <button type="submit">Delete</button>
    </form>
{% endif %}
```

### Assignment Due Date Display
```html
{% if assignment.due_date %}
    <p>Due: {{ assignment.due_date }}</p>
    {% if now > assignment.due_date %}
        <span class="badge badge-danger">Overdue</span>
    {% else %}
        <span class="badge badge-info">{{ days_until|default:"Today" }}</span>
    {% endif %}
{% endif %}
```

---

## Common Issues and Solutions

### Issue: Join key not generated for existing classrooms
**Solution**: Run `python manage.py generate_join_keys`

### Issue: "is_edited" field not showing
**Solution**: 
```html
{% if comment.is_edited %}
    <span class="text-muted">(edited at {{ comment.updated_at }})</span>
{% endif %}
```

### Issue: Permissions not checking correctly
**Solution**: Always validate:
```python
is_author = user == object.author
is_teacher = user == classroom.teacher
if not (is_author or is_teacher):
    return redirect('home')
```

---

## Performance Considerations

1. **Search**: Add database indexes on frequently searched fields
   ```python
   class Meta:
       indexes = [
           models.Index(fields=['name']),
           models.Index(fields=['teacher']),
       ]
   ```

2. **Submissions**: Use `select_related()` and `prefetch_related()` in queries

3. **Comments**: Consider pagination for large comment threads

---

## Next Phase Features

After these core features are implemented, consider:
- Advanced analytics dashboard
- Email notifications
- Discussion forums per classroom
- Resource file uploads
- Real-time collaboration features
