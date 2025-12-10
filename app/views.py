from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Question, Answer, Tag
from .utils import paginate, handle_login, handle_signup, prepare_profile_context


def _get_questions_with_pagination(questions_queryset, request, per_page=10):
    questions = questions_queryset.select_related('author').prefetch_related('tags')
    page = paginate(questions, request, per_page=per_page)
    return page


def index(request):
    questions = Question.objects.new()
    page = _get_questions_with_pagination(questions, request)
    return render(request, 'index.html', {'page': page, 'questions': page.object_list})


def hot(request):
    questions = Question.objects.best()
    page = _get_questions_with_pagination(questions, request)
    return render(request, 'hot.html', {'page': page, 'questions': page.object_list})


def tag(request, tag_name):
    tag_obj = get_object_or_404(Tag, name=tag_name)
    questions = Question.objects.by_tag(tag_name)
    page = _get_questions_with_pagination(questions, request)
    return render(request, 'tag.html', {'tag_name': tag_name, 'page': page, 'questions': page.object_list})


def question(request, question_id):
    question_obj = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('tags'),
        id=question_id
    )
    answers = question_obj.answers.select_related('author').order_by('-is_correct', '-created_at')
    answers_page = paginate(answers, request, per_page=10)
    return render(request, 'question.html', {
        'question': question_obj,
        'answers_page': answers_page,
        'answers': answers_page.object_list
    })


def ask(request):
    if request.method == 'POST':
        return redirect('index')
    return render(request, 'ask.html')


def login_view(request):
    if request.method == 'POST' and handle_login(request):
            return redirect('index')
    return render(request, 'login.html')


def signup(request):
    if request.method == 'POST' and handle_signup(request):
            return redirect('login')
    return render(request, 'signup.html')


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    context = prepare_profile_context(profile_user, request)
    return render(request, 'profile.html', context)
    