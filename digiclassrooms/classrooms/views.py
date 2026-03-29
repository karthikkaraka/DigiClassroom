from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Classroom
from .forms import ClassroomForm, JoinClassroomForm

@login_required(login_url='login')
def home(request):
    try:
        if request.user.profile.is_teacher:
            return redirect('teacher_dashboard')
        else:
            return redirect('student_dashboard')
    except:
        return redirect('student_dashboard')

@login_required(login_url='login')
def teacher_dashboard(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_teacher:
        return redirect('student_dashboard')
        
    try:
        classroom = request.user.teaching_classroom
        notices = classroom.notices.all().order_by('-created_at')[:5]
        lectures = classroom.lectures.all().order_by('-created_at')[:5]
        assignments = classroom.assignments.all().order_by('-created_at')[:5]
    except Classroom.DoesNotExist:
        return redirect('setup_classroom')
        
    return render(request, 'classrooms/teacher_home.html', {
        'classroom': classroom,
        'notices': notices,
        'lectures': lectures,
        'assignments': assignments,
    })

@login_required(login_url='login')
def student_dashboard(request):
    enrolled_classrooms = request.user.enrolled_classrooms.all()
    available_classrooms = Classroom.objects.exclude(students=request.user)
    return render(request, 'classrooms/student_home.html', {
        'enrolled_classrooms': enrolled_classrooms,
        'available_classrooms': available_classrooms
    })

@login_required(login_url='login')
def setup_classroom(request):
    if not request.user.profile.is_teacher:
        return redirect('home')
    
    if hasattr(request.user, 'teaching_classroom'):
        return redirect('teacher_dashboard')

    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            classroom.teacher = request.user
            classroom.save()
            return redirect('teacher_dashboard')
    else:
        form = ClassroomForm()
    return render(request, 'classrooms/setup_classroom.html', {'form': form})

@login_required(login_url='login')
def enroll_classroom(request):
    # Backward-compatible endpoint: redirect to the key-based join flow.
    return redirect('join_classroom')


@login_required(login_url='login')
def join_classroom(request, pk=None):
    """Join a classroom using its time-limited join key."""
    if hasattr(request.user, 'profile') and getattr(request.user.profile, 'is_teacher', False):
        messages.error(request, 'Teachers cannot join classrooms as students.')
        return redirect('teacher_dashboard')

    classroom = None
    if pk is not None:
        classroom = get_object_or_404(Classroom, pk=pk)

    if request.method == 'POST':
        form = JoinClassroomForm(request.POST)
        if form.is_valid():
            join_key = form.cleaned_data['join_key']

            target_classroom = classroom
            if target_classroom is None:
                target_classroom = Classroom.objects.filter(join_key__iexact=join_key).first()

            if not target_classroom:
                messages.error(request, 'Invalid join key.')
                return redirect('join_classroom')

            if not target_classroom.is_join_key_valid(join_key):
                if target_classroom.join_key_expires_at and timezone.now() > target_classroom.join_key_expires_at:
                    messages.error(request, 'That join key has expired. Ask your teacher for a new key.')
                else:
                    messages.error(request, 'Invalid join key for this classroom.')
                return redirect('join_classroom_for_classroom', pk=target_classroom.pk)

            target_classroom.students.add(request.user)
            messages.success(request, f'Joined "{target_classroom.name}" successfully!')
            return redirect('classroom_detail', pk=target_classroom.pk)
    else:
        form = JoinClassroomForm()

    return render(request, 'classrooms/join_classroom.html', {
        'form': form,
        'classroom': classroom,
    })


@login_required(login_url='login')
def regenerate_join_key(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if not hasattr(request.user, 'profile') or not request.user.profile.is_teacher or request.user != classroom.teacher:
        messages.error(request, 'Only the classroom teacher can regenerate the join key.')
        return redirect('home')

    if request.method != 'POST':
        return redirect('teacher_dashboard')

    classroom.regenerate_join_key()
    messages.success(
        request,
        f'New join key generated: {classroom.join_key} (expires at {classroom.join_key_expires_at:%Y-%m-%d %H:%M UTC})'
    )
    return redirect('teacher_dashboard')

@login_required(login_url='login')
def classroom_detail(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    is_teacher = request.user == classroom.teacher
    is_student = request.user in classroom.students.all()
    
    if not (is_teacher or is_student):
        return redirect('student_dashboard')

    context = {
        'classroom': classroom,
        'is_teacher': is_teacher,
    }
    return render(request, 'classrooms/classroom_detail.html', context)

@login_required(login_url='login')
def classroom_notices(request, pk):
    return redirect('notices_list', classroom_pk=pk)

@login_required(login_url='login')
def classroom_lectures(request, pk):
    return redirect('lectures_list', classroom_pk=pk)

@login_required(login_url='login')
def classroom_assignments(request, pk):
    return redirect('assignments_list', classroom_pk=pk)

@login_required(login_url='login')
def search_classrooms(request):
    """Search available classrooms by name, description, or teacher"""
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
    paginator = Paginator(classrooms, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'classrooms/search.html', {
        'page_obj': page_obj,
        'query': query
    })
