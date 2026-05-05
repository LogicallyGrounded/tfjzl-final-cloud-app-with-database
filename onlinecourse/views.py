from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from .models import Course, Lesson, Enrollment, Question, Choice, Submission
from django.urls import reverse
from django.views import generic
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'
    def get_queryset(self):
        return Course.objects.order_by('-pub_date')

class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'

def enroll(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, pk=course_id)
        # Create enrollment
        Enrollment.objects.create(user=request.user, course=course)
        return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course.id,)))

def login_request(request):
    if request.method == 'POST':
        username = request.POST['username']
        psw = request.POST['psw']
        user = authenticate(username=username, password=psw)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            return redirect('onlinecourse:index')
    return redirect('onlinecourse:index')

def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')

def registration(request):
    if request.method == 'POST':
        try:
            User.objects.create_user(username=request.POST['username'], password=request.POST['psw'], first_name=request.POST['first_name'], last_name=request.POST['last_name'])
            user = authenticate(username=request.POST['username'], password=request.POST['psw'])
            login(request, user)
            return redirect('onlinecourse:index')
        except:
            return redirect('onlinecourse:registration')
    return render(request, 'onlinecourse/registration_bootstrap.html')

# --- EXAM LOGIC ---
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    
    # FIX: Safely grab the first enrollment if duplicates exist
    enrollment = Enrollment.objects.filter(user=user, course=course).first()
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