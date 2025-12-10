from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Question, Answer, Tag
from .forms import LoginForm, SignupForm, ProfileEditForm, QuestionForm, AnswerForm
from .utils import paginate, prepare_profile_context


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


def question_view(request, question_id):
    question_obj = get_object_or_404(
        Question.objects.select_related('author').prefetch_related('tags'),
        id=question_id
    )
    answers = question_obj.answers.select_related('author').order_by('-is_correct', '-created_at')
    answers_page = paginate(answers, request, per_page=10)
    
    answer_form = AnswerForm()
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?continue={request.path}")
        
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit=False, question=question_obj, author=request.user)
            answer.save()
            all_answers = list(question_obj.answers.select_related('author').order_by('-is_correct', '-created_at'))
            try:
                answer_index = all_answers.index(answer)
                page_number = (answer_index // 10) + 1
            except (ValueError, IndexError):
                page_number = 1

            return redirect(f"{question_obj.get_url()}?page={page_number}#answer-{answer.id}")
    
    return render(request, 'question.html', {
        'question': question_obj,
        'answers_page': answers_page,
        'answers': answers_page.object_list,
        'answer_form': answer_form,
    })


def ask(request):
    if not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?continue={request.path}")
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=True, author=request.user)
            return redirect(question.get_url())
    else:
        form = QuestionForm()
    
    return render(request, 'ask.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    next_url = request.GET.get('continue', None)
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        post_next = request.POST.get('next', next_url)
        if post_next:
            next_url = post_next
            
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if next_url:
                    if next_url.startswith('/'):
                        return redirect(next_url)
                    try:
                        from django.urls import reverse
                        return redirect(next_url)
                    except:
                        pass
                return redirect('index')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form, 'next_url': next_url})


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignupForm()
    
    return render(request, 'signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def profile_edit(request):
    from .models import Profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile_edit')
    else:
        form = ProfileEditForm(instance=profile, user=request.user)
        if not form.initial.get('first_name') and request.user.first_name:
            form.initial['first_name'] = request.user.first_name
        if not form.initial.get('email') and request.user.email:
            form.initial['email'] = request.user.email
    
    return render(request, 'profile_edit.html', {'form': form, 'user': request.user})


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    context = prepare_profile_context(profile_user, request)
    return render(request, 'profile.html', context)
