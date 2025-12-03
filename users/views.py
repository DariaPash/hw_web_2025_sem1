from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from app.views import paginate


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
    
    return render(request, 'login.html')


def signup(request):
    """Страница регистрации"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password == password2:
            User.objects.create_user(username=username, email=email, password=password)
            return redirect('login')
    
    return render(request, 'signup.html')


def profile(request, username):
    """Страница профиля пользователя"""
    from datetime import datetime, timedelta
    fake_user = type('User', (), {
        'username': username,
        'email': f'{username}@example.com',
        'date_joined': datetime.now() - timedelta(days=30),
    })()

    from app.views import get_fake_questions
    fake_questions = get_fake_questions()
    user_questions = [q for q in fake_questions if q['author'] == username]

    if not user_questions:
        user_questions = [
            {
                'id': 1,
                'title': 'Как правильно настроить Django проект с PostgreSQL?',
                'preview': 'Я начинающий разработчик и хочу создать новый Django проект с использованием PostgreSQL в качестве базы данных...',
                'votes_up': 15,
                'votes_down': 3,
                'answers_count': 5,
                'time_ago': '2 часа назад',
                'tags': ['django', 'postgresql', 'python']
            },
            {
                'id': 2,
                'title': 'Как работать с виртуальными окружениями в Python?',
                'preview': 'Можете объяснить, как правильно создавать и использовать виртуальные окружения в Python?',
                'votes_up': 8,
                'votes_down': 1,
                'answers_count': 3,
                'time_ago': '1 день назад',
                'tags': ['python', 'virtualenv', 'pip']
            },
        ]

    questions_page = paginate(user_questions, request, per_page=10)
    
    fake_answers = [
        {
            'id': 1,
            'text': 'Для начала установите psycopg2 или psycopg2-binary через pip. Затем в settings.py настройте DATABASES. Используйте миграции для создания таблиц.',
            'question_id': 1,
            'question_title': 'Как правильно настроить Django проект с PostgreSQL?',
            'time_ago': '1 час назад',
            'votes_up': 8,
            'votes_down': 0,
            'is_correct': True,
        },
        {
            'id': 2,
            'text': 'Также рекомендую использовать переменные окружения для хранения паролей и настроек БД. Это более безопасно.',
            'question_id': 1,
            'question_title': 'Как правильно настроить Django проект с PostgreSQL?',
            'time_ago': '2 часа назад',
            'votes_up': 5,
            'votes_down': 1,
            'is_correct': False,
        },
        {
            'id': 3,
            'text': 'Виртуальные окружения позволяют изолировать зависимости проекта. Используйте команду: python -m venv venv',
            'question_id': 2,
            'question_title': 'Как работать с виртуальными окружениями в Python?',
            'time_ago': '3 часа назад',
            'votes_up': 12,
            'votes_down': 0,
            'is_correct': True,
        },
    ]

    user_answers = fake_answers if username in ['john_doe', 'django_expert', 'security_guru', 'python_guru'] else fake_answers[:2]
    answers_page = paginate(user_answers, request, per_page=10)

    stats = {
        'reputation': 156,
        'questions_count': len(user_questions),
        'answers_count': len(user_answers),
        'accepted_answers': 12,
    }
    
    return render(request, 'profile.html', {
        'profile_user': fake_user,
        'stats': stats,
        'questions_page': questions_page,
        'user_questions': questions_page.object_list,
        'answers_page': answers_page,
        'user_answers': answers_page.object_list,
    })

