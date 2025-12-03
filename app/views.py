from django.shortcuts import render, redirect
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def get_fake_questions():
    """Вспомогательная функция для получения списка фейковых вопросов"""
    return [
        {
            'id': 1,
            'title': 'Как правильно настроить Django проект с PostgreSQL?',
            'preview': 'Я начинающий разработчик и хочу создать новый Django проект с использованием PostgreSQL в качестве базы данных. Не могли бы вы подсказать правильную последовательность действий для настройки...',
            'full_text': 'Я начинающий разработчик и хочу создать новый Django проект с использованием PostgreSQL в качестве базы данных. Не могли бы вы подсказать правильную последовательность действий для настройки? Мне нужно понять, как правильно установить драйвер, настроить settings.py и создать миграции.',
            'author': 'john_doe',
            'author_name': 'john_doe',
            'time_ago': '2 часа назад',
            'votes_up': 15,
            'votes_down': 3,
            'answers_count': 5,
            'tags': ['django', 'postgresql', 'python']
        },
        {
            'id': 2,
            'title': 'Разница между let, const и var в JavaScript',
            'preview': 'Можете объяснить, в чем основные различия между объявлением переменных через let, const и var в JavaScript? Когда какую использовать и какие есть особенности областей видимости?',
            'full_text': 'Можете объяснить, в чем основные различия между объявлением переменных через let, const и var в JavaScript? Когда какую использовать и какие есть особенности областей видимости? Особенно интересует поведение в циклах и функциях.',
            'author': 'jane_smith',
            'author_name': 'jane_smith',
            'time_ago': '4 часа назад',
            'votes_up': 11,
            'votes_down': 3,
            'answers_count': 3,
            'tags': ['javascript', 'es6']
        },
        {
            'id': 3,
            'title': 'Как создать адаптивный дизайн с помощью CSS Grid?',
            'preview': 'Подскажите, как лучше всего использовать CSS Grid для создания адаптивного макета? Хочу понять основные принципы и получить примеры кода для разных разрешений экрана.',
            'full_text': 'Подскажите, как лучше всего использовать CSS Grid для создания адаптивного макета? Хочу понять основные принципы и получить примеры кода для разных разрешений экрана. Также интересует, как сочетать Grid с Flexbox.',
            'author': 'alex_dev',
            'author_name': 'alex_dev',
            'time_ago': '6 часов назад',
            'votes_up': 18,
            'votes_down': 3,
            'answers_count': 7,
            'tags': ['css', 'css-grid', 'responsive']
        },
        {
            'id': 4,
            'title': 'Как работает асинхронное программирование в Python?',
            'preview': 'Хочу разобраться с async/await в Python. Можете объяснить основные концепции и показать примеры использования? Как это работает под капотом?',
            'full_text': 'Хочу разобраться с async/await в Python. Можете объяснить основные концепции и показать примеры использования? Как это работает под капотом? В чем разница между async и threading?',
            'author': 'python_guru',
            'author_name': 'python_guru',
            'time_ago': '8 часов назад',
            'votes_up': 22,
            'votes_down': 1,
            'answers_count': 12,
            'tags': ['python', 'async', 'asyncio']
        },
        {
            'id': 5,
            'title': 'Что такое REST API и как его правильно проектировать?',
            'preview': 'Нужно создать REST API для моего проекта. Какие принципы нужно соблюдать? Как правильно организовать endpoints и структуру данных?',
            'full_text': 'Нужно создать REST API для моего проекта. Какие принципы нужно соблюдать? Как правильно организовать endpoints и структуру данных? Также интересует вопрос версионирования API и обработки ошибок.',
            'author': 'backend_master',
            'author_name': 'backend_master',
            'time_ago': '10 часов назад',
            'votes_up': 9,
            'votes_down': 2,
            'answers_count': 4,
            'tags': ['rest', 'api', 'backend']
        },
        {
            'id': 6,
            'title': 'Как оптимизировать запросы к базе данных в Django?',
            'preview': 'У меня есть Django приложение, которое делает много запросов к БД. Как можно оптимизировать производительность? Что такое select_related и prefetch_related?',
            'full_text': 'У меня есть Django приложение, которое делает много запросов к БД. Как можно оптимизировать производительность? Что такое select_related и prefetch_related? Когда использовать индексы и как правильно их создавать?',
            'author': 'django_pro',
            'author_name': 'django_pro',
            'time_ago': '12 часов назад',
            'votes_up': 14,
            'votes_down': 4,
            'answers_count': 8,
            'tags': ['django', 'optimization', 'database']
        },
        {
            'id': 7,
            'title': 'Разница между React и Vue.js',
            'preview': 'Планирую изучить один из фреймворков для фронтенда. Можете сравнить React и Vue.js? В чем их основные различия и когда что использовать?',
            'full_text': 'Планирую изучить один из фреймворков для фронтенда. Можете сравнить React и Vue.js? В чем их основные различия и когда что использовать? Также интересно узнать о производительности и экосистеме каждого из них.',
            'author': 'frontend_dev',
            'author_name': 'frontend_dev',
            'time_ago': '14 часов назад',
            'votes_up': 7,
            'votes_down': 5,
            'answers_count': 6,
            'tags': ['react', 'vue', 'javascript', 'frontend']
        },
        {
            'id': 8,
            'title': 'Как правильно работать с Git и GitHub?',
            'preview': 'Начал изучать Git, но не уверен, что делаю все правильно. Какие основные команды нужно знать? Как правильно организовывать ветки и коммиты?',
            'full_text': 'Начал изучать Git, но не уверен, что делаю все правильно. Какие основные команды нужно знать? Как правильно организовывать ветки и коммиты? Также интересует работа с pull requests и merge конфликтами.',
            'author': 'git_newbie',
            'author_name': 'git_newbie',
            'time_ago': '1 день назад',
            'votes_up': 19,
            'votes_down': 2,
            'answers_count': 9,
            'tags': ['git', 'github', 'version-control']
        },
        {
            'id': 9,
            'title': 'Что такое Docker и зачем он нужен?',
            'preview': 'Слышал про Docker, но не совсем понимаю, что это такое и зачем он нужен. Можете объяснить простыми словами и показать примеры использования?',
            'full_text': 'Слышал про Docker, но не совсем понимаю, что это такое и зачем он нужен. Можете объяснить простыми словами и показать примеры использования? Как создать Dockerfile и docker-compose.yml?',
            'author': 'devops_learner',
            'author_name': 'devops_learner',
            'time_ago': '1 день назад',
            'votes_up': 13,
            'votes_down': 3,
            'answers_count': 5,
            'tags': ['docker', 'devops', 'containers']
        },
        {
            'id': 10,
            'title': 'Как тестировать код в Python?',
            'preview': 'Хочу начать писать тесты для своего Python проекта. С чего начать? Какие библиотеки использовать? Как правильно организовать тесты?',
            'full_text': 'Хочу начать писать тесты для своего Python проекта. С чего начать? Какие библиотеки использовать? Как правильно организовать тесты? Интересуют unit тесты, интеграционные тесты и mocking.',
            'author': 'test_enthusiast',
            'author_name': 'test_enthusiast',
            'time_ago': '1 день назад',
            'votes_up': 16,
            'votes_down': 1,
            'answers_count': 7,
            'tags': ['python', 'testing', 'pytest', 'unittest']
        },
        {
            'id': 11,
            'title': 'Как работает виртуальная память в операционных системах?',
            'preview': 'Изучаю операционные системы. Можете объяснить концепцию виртуальной памяти? Как она связана с физической памятью и как работает подкачка?',
            'full_text': 'Изучаю операционные системы. Можете объяснить концепцию виртуальной памяти? Как она связана с физической памятью и как работает подкачка? Также интересно узнать про страничную организацию памяти.',
            'author': 'os_student',
            'author_name': 'os_student',
            'time_ago': '2 дня назад',
            'votes_up': 8,
            'votes_down': 4,
            'answers_count': 3,
            'tags': ['operating-systems', 'memory', 'computer-science']
        },
        {
            'id': 12,
            'title': 'Как создать микросервисную архитектуру?',
            'preview': 'Планирую перейти с монолитной архитектуры на микросервисы. Какие принципы нужно соблюдать? С какими проблемами можно столкнуться?',
            'full_text': 'Планирую перейти с монолитной архитектуры на микросервисы. Какие принципы нужно соблюдать? С какими проблемами можно столкнуться? Как организовать коммуникацию между сервисами и управление данными?',
            'author': 'architect_pro',
            'author_name': 'architect_pro',
            'time_ago': '2 дня назад',
            'votes_up': 20,
            'votes_down': 6,
            'answers_count': 11,
            'tags': ['microservices', 'architecture', 'design']
        },
        {
            'id': 13,
            'title': 'Как работает HTTPS и SSL/TLS?',
            'preview': 'Хочу понять, как обеспечивается безопасность в HTTPS. Как работает процесс handshake? Что такое SSL и TLS?',
            'full_text': 'Хочу понять, как обеспечивается безопасность в HTTPS. Как работает процесс handshake? Что такое SSL и TLS? Как получить и установить SSL сертификат для своего сайта?',
            'author': 'security_learner',
            'author_name': 'security_learner',
            'time_ago': '2 дня назад',
            'votes_up': 10,
            'votes_down': 2,
            'answers_count': 4,
            'tags': ['https', 'ssl', 'tls', 'security']
        },
        {
            'id': 14,
            'title': 'Как оптимизировать производительность веб-приложения?',
            'preview': 'Мое веб-приложение работает медленно. Какие методы оптимизации можно использовать? Как измерить производительность и найти узкие места?',
            'full_text': 'Мое веб-приложение работает медленно. Какие методы оптимизации можно использовать? Как измерить производительность и найти узкие места? Интересует кэширование, оптимизация запросов и фронтенда.',
            'author': 'performance_guru',
            'author_name': 'performance_guru',
            'time_ago': '3 дня назад',
            'votes_up': 12,
            'votes_down': 3,
            'answers_count': 6,
            'tags': ['performance', 'optimization', 'web']
        },
        {
            'id': 15,
            'title': 'Как правильно структурировать проект на Django?',
            'preview': 'Создаю новый проект на Django. Как лучше организовать структуру папок? Где размещать логику приложения, где модели, где views?',
            'full_text': 'Создаю новый проект на Django. Как лучше организовать структуру папок? Где размещать логику приложения, где модели, где views? Какие best practices существуют для организации Django проектов?',
            'author': 'django_student',
            'author_name': 'django_student',
            'time_ago': '3 дня назад',
            'votes_up': 17,
            'votes_down': 2,
            'answers_count': 8,
            'tags': ['django', 'project-structure', 'best-practices']
        },
    ]


def index(request):
    """Список новых вопросов (главная страница)"""
    fake_questions = get_fake_questions()
    page = paginate(fake_questions, request, per_page=10)
    
    return render(request, 'index.html', {
        'page': page,
        'questions': page.object_list,  
    })


def hot(request):
    """Список лучших вопросов"""
    fake_questions = get_fake_questions()
    fake_questions = sorted(fake_questions, key=lambda x: x['votes_up'] - x['votes_down'], reverse=True)
    page = paginate(fake_questions, request, per_page=10)
    
    return render(request, 'hot.html', {
        'page': page,
        'questions': page.object_list,
    })


def question(request, question_id):
    """Страница одного вопроса со списком ответов"""
    fake_questions = get_fake_questions()
    question_data = next((q for q in fake_questions if q['id'] == question_id), None)
    
    if question_data is None:
        raise Http404("Вопрос не найден")
    fake_answers = [
        {
            'id': 1,
            'text': 'Для начала установите psycopg2 или psycopg2-binary через pip. Затем в settings.py настройте DATABASES. Используйте миграции для создания таблиц.',
            'author': 'django_expert',
            'author_name': 'django_expert',
            'time_ago': '1 час назад',
            'votes_up': 8,
            'votes_down': 0,
            'is_correct': True,
        },
        {
            'id': 2,
            'text': 'Также рекомендую использовать переменные окружения для хранения паролей и настроек БД. Это более безопасно.',
            'author': 'security_guru',
            'author_name': 'security_guru',
            'time_ago': '2 часа назад',
            'votes_up': 5,
            'votes_down': 1,
            'is_correct': False,
        },
        {
            'id': 3,
            'text': 'Не забудьте создать суперпользователя командой python manage.py createsuperuser после настройки БД.',
            'author': 'admin_helper',
            'author_name': 'admin_helper',
            'time_ago': '3 часа назад',
            'votes_up': 3,
            'votes_down': 0,
            'is_correct': False,
        },
    ]
    
    return render(request, 'question.html', {
        'question': question_data,
        'answers': fake_answers,
    })


def ask(request):
    """Форма создания вопроса"""
    if request.method == 'POST':
        return redirect('index')
    
    return render(request, 'ask.html')


def search(request):
    """Заглушка для страницы поиска"""
    query = request.GET.get('q', '')
    return render(request, 'search.html', {
        'query': query,
    })


def tag(request, tag_name):
    """Список вопросов по тегу"""
    fake_questions = get_fake_questions()
    filtered_questions = [q for q in fake_questions if tag_name in q['tags']]
    page = paginate(filtered_questions, request, per_page=10)
    
    return render(request, 'tag.html', {
        'tag_name': tag_name,
        'page': page,
        'questions': page.object_list,
    })



def paginate(objects_list, request, per_page=10):
    """
    Функция для пагинации списка объектов.
    
    Args:
        objects_list: список объектов или QuerySet для пагинации
        request: объект запроса Django
        per_page: количество элементов на странице (по умолчанию 10)
    
    Returns:
        page: объект Page из Django Paginator с данными текущей страницы
    """
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
    