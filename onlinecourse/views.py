from .models import Question, Choice, Submission
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Course, Lesson, Enrollment, Question, Choice, Submission

def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    
    # Extract selected choice IDs from POST request
    choices = []
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            choices.append(get_object_or_404(Choice, pk=int(value)))
    
    submission.choices.set(choices)
    submission_id = submission.id
    
    return HttpResponseRedirect(reverse('onlinecourse:show_exam_result', args=(course_id, submission_id,)))

def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    selected_choices = submission.choices.all()
    total_score = 0
    questions = course.question_set.all()
    
    for question in questions:
        # Get IDs of selected choices belonging to this specific question
        selected_ids = selected_choices.filter(question=question).values_list('id', flat=True)
        if question.is_get_score(selected_ids):
            total_score += question.grade
            
    context['course'] = course
    context['grade'] = total_score
    context['choices'] = selected_choices
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    enrollment = Enrollment.objects.get(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    
    choices = []
    for key, value in request.POST.items():
        if key.startswith('choice_'):
            choices.append(get_object_or_404(Choice, pk=int(value)))
    
    submission.choices.set(choices)
    submission_id = submission.id
    
    return HttpResponseRedirect(reverse('onlinecourse:show_exam_result', args=(course_id, submission_id,)))

def show_exam_result(request, course_id, submission_id):
    context = {}
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    selected_choices = submission.choices.all()
    total_score = 0
    questions = course.question_set.all()
    
    for question in questions:
        selected_ids = selected_choices.filter(question=question).values_list('id', flat=True)
        if question.is_get_score(selected_ids):
            total_score += question.grade
            
    context['course'] = course
    context['grade'] = total_score
    context['choices'] = selected_choices
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)
