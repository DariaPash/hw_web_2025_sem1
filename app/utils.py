from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page')
 
    if page_number is None:
        page_number = 1
    else:
        try:
            page_number = int(page_number)
            if page_number < 1:
                page_number = 1
        except (ValueError, TypeError):
            page_number = 1
    
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    
    return page


def handle_login(request):
    username = request.POST.get('username', '').strip()
    password = request.POST.get('password', '')
    
    if not username or not password:
        return None
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('index')
    return None


def handle_signup(request):
    username = request.POST.get('username', '').strip()
    email = request.POST.get('email', '').strip()
    password = request.POST.get('password', '')
    password2 = request.POST.get('password2', '')
    
    if not username or not email or not password or not password2:
        return None
    
    if password == password2:
        try:
            User.objects.create_user(username=username, email=email, password=password)
            return redirect('login')
        except Exception:
            return None
    return None


def get_user_profile_data(user):
    from .models import Question, Answer
    user_questions = Question.objects.by_author(user.username)
    user_answers = Answer.objects.filter(author=user)
    stats = user.profile.get_stats() if hasattr(user, 'profile') else {
        'reputation': 0, 'questions_count': 0, 'answers_count': 0, 'accepted_answers': 0
    }
    return {
        'user_questions': user_questions,
        'user_answers': user_answers,
        'stats': stats,
    }


def prepare_profile_context(profile_user, request):
    profile_data = get_user_profile_data(profile_user)
    questions_page = paginate(profile_data['user_questions'], request, per_page=10)
    answers_page = paginate(profile_data['user_answers'], request, per_page=10)
    return {
        'profile_user': profile_user,
        'stats': profile_data['stats'],
        'questions_page': questions_page,
        'user_questions': questions_page.object_list,
        'answers_page': answers_page,
        'user_answers': answers_page.object_list,
    }

