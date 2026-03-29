from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import math
from classrooms.models import Classroom
from .models import Assignment, Question, Choice, Submission, StudentAnswer, SubmissionDraft
from .forms import AssignmentForm, QuestionForm

@login_required(login_url='login')
def assignment_list(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    assignments = classroom.assignments.all().order_by('-created_at')
    is_teacher = request.user == classroom.teacher
    return render(request, 'assignments/assignment_list.html', {
        'classroom': classroom, 'assignments': assignments, 'is_teacher': is_teacher
    })

@login_required(login_url='login')
def assignment_create(request, classroom_pk):
    classroom = get_object_or_404(Classroom, pk=classroom_pk)
    if request.user != classroom.teacher:
        return redirect('assignment_list', classroom_pk=classroom.pk)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.classroom = classroom
            assignment.save()
            return redirect('assignment_detail', pk=assignment.pk)
    else:
        form = AssignmentForm()
    return render(request, 'assignments/assignment_form.html', {'form': form, 'classroom': classroom})

@login_required(login_url='login')
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    is_teacher = request.user == assignment.classroom.teacher
    questions = assignment.questions.all()
    
    submission = None
    submissions = None
    attempts_used = 0
    attempts_left = 0
    can_attempt = False
    is_late_now = bool(assignment.due_date and timezone.now() > assignment.due_date)

    if not is_teacher:
        submissions = Submission.objects.filter(assignment=assignment, student=request.user).order_by('-attempt_number', '-submitted_at')
        submission = submissions.first()
        attempts_used = submissions.count()
        attempts_left = max(assignment.max_attempts - attempts_used, 0)
        can_attempt = attempts_left > 0

        if is_late_now and assignment.late_submission_policy == Assignment.LATE_POLICY_DENY:
            can_attempt = False
        
    return render(request, 'assignments/assignment_detail.html', {
        'assignment': assignment,
        'is_teacher': is_teacher,
        'questions': questions,
        'submission': submission,
        'submissions': submissions,
        'attempts_used': attempts_used,
        'attempts_left': attempts_left,
        'can_attempt': can_attempt,
        'is_late_now': is_late_now,
    })

@login_required(login_url='login')
def add_question(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.user != assignment.classroom.teacher:
        return redirect('assignment_detail', pk=pk)
        
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = Question.objects.create(assignment=assignment, text=form.cleaned_data['question_text'])
            opts = [
                (form.cleaned_data['option1'], '1'),
                (form.cleaned_data['option2'], '2'),
                (form.cleaned_data['option3'], '3'),
                (form.cleaned_data['option4'], '4'),
            ]
            correct = form.cleaned_data['correct_option']
            for text, idx in opts:
                Choice.objects.create(question=question, text=text, is_correct=(idx == correct))
            return redirect('assignment_detail', pk=pk)
    else:
        form = QuestionForm()
    return render(request, 'assignments/add_question.html', {'form': form, 'assignment': assignment})

@login_required(login_url='login')
def take_assignment(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.user == assignment.classroom.teacher:
        return redirect('assignment_detail', pk=pk)

    existing_attempts = Submission.objects.filter(assignment=assignment, student=request.user).count()
    if existing_attempts >= assignment.max_attempts:
        messages.error(request, 'No attempts remaining for this assignment.')
        return redirect('assignment_detail', pk=pk)

    is_late = bool(assignment.due_date and timezone.now() > assignment.due_date)
    if is_late and assignment.late_submission_policy == Assignment.LATE_POLICY_DENY:
        messages.error(request, 'This assignment is closed because the due date has passed.')
        return redirect('assignment_detail', pk=pk)

    draft, _ = SubmissionDraft.objects.get_or_create(assignment=assignment, student=request.user)
        
    if request.method == 'POST':
        action = request.POST.get('action', 'submit')
        selected_answers = {}

        for question in assignment.questions.all():
            choice_id = request.POST.get(f'question_{question.id}')
            if choice_id:
                selected_answers[str(question.id)] = int(choice_id)

        if action == 'save_draft':
            draft.answers = selected_answers
            draft.save(update_fields=['answers', 'updated_at'])
            messages.success(request, 'Draft saved.')
            return redirect('take_assignment', pk=pk)

        score = 0
        submission = Submission.objects.create(
            assignment=assignment,
            student=request.user,
            attempt_number=existing_attempts + 1,
            is_late=is_late,
        )
        
        for question in assignment.questions.all():
            choice_id = request.POST.get(f'question_{question.id}')
            if choice_id:
                choice = Choice.objects.filter(question=question, pk=choice_id).first()
                if not choice:
                    continue
                StudentAnswer.objects.create(submission=submission, question=question, choice=choice)
                if choice.is_correct:
                    score += 1
        
        penalty_percent = 0
        if is_late and assignment.late_submission_policy == Assignment.LATE_POLICY_PENALTY:
            penalty_percent = assignment.late_penalty_percent
            score = max(0, score - math.ceil(score * (penalty_percent / 100)))

        submission.score = score
        submission.late_penalty_percent = penalty_percent
        submission.save()
        draft.delete()
        messages.success(request, 'Assignment submitted successfully.')
        return redirect('assignment_detail', pk=pk)

    draft_answers = draft.answers if isinstance(draft.answers, dict) else {}
    return render(request, 'assignments/take_assignment.html', {
        'assignment': assignment,
        'draft_answers': draft_answers,
    })

@login_required(login_url='login')
def view_submissions(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if request.user != assignment.classroom.teacher:
        return redirect('home')
    submissions = assignment.submissions.all().order_by('-submitted_at')
    return render(request, 'assignments/view_submissions.html', {'assignment': assignment, 'submissions': submissions})

@login_required(login_url='login')
def submission_detail(request, pk):
    submission = get_object_or_404(Submission, pk=pk)
    is_teacher = request.user == submission.assignment.classroom.teacher
    is_student = request.user == submission.student
    
    if not (is_teacher or is_student):
        return redirect('home')
        
    if request.method == 'POST' and is_teacher:
        feedback = request.POST.get('feedback')
        submission.teacher_feedback = feedback
        submission.save()
        return redirect('submission_detail', pk=pk)
        
    answers = submission.answers.all() # type: ignore
    return render(request, 'assignments/submission_detail.html', {
        'submission': submission,
        'answers': answers,
        'is_teacher': is_teacher
    })

@login_required(login_url='login')
def edit_assignment(request, pk):
    """Edit an assignment"""
    assignment = get_object_or_404(Assignment, pk=pk)
    
    # Check permission: only teacher can edit
    if request.user != assignment.classroom.teacher:
        return redirect('assignment_detail', pk=pk)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.updated_at = __import__('django.utils.timezone', fromlist=['now']).now()
            assignment.save()
            return redirect('assignment_detail', pk=pk)
    else:
        form = AssignmentForm(instance=assignment)
    
    return render(request, 'assignments/assignment_form.html', {
        'form': form,
        'assignment': assignment,
        'classroom': assignment.classroom,
        'edit': True
    })

@login_required(login_url='login')
def delete_assignment(request, pk):
    """Delete an assignment"""
    assignment = get_object_or_404(Assignment, pk=pk)
    classroom = assignment.classroom
    
    # Check permission: only teacher can delete
    if request.user != classroom.teacher:
        return redirect('assignment_detail', pk=pk)
    
    if request.method == 'POST':
        assignment.delete()
        return redirect('assignment_list', classroom_pk=classroom.pk)
    
    return render(request, 'assignments/delete_assignment.html', {'assignment': assignment})
