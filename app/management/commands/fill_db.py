from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.db import models
from datetime import timedelta
import random
from app.models import Tag, Question, Answer, QuestionLike, AnswerLike, Profile


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def add_arguments(self, parser):
        parser.add_argument(
            'ratio',
            type=int,
            help='Коэффициент заполнения (пользователей = ratio, вопросов = ratio * 10, и т.д.)'
        )

    def handle(self, *args, **options):
        ratio = options['ratio']
        self.stdout.write(self.style.SUCCESS(f'Начинаем заполнение базы данных с ratio={ratio}'))
        
        num_users = ratio
        num_tags = ratio
        num_questions = ratio * 10
        num_answers = ratio * 100
        num_likes = ratio * 200
        
        self.stdout.write(f'Создание {num_users} пользователей...')
        users = self.create_users(num_users)
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {len(users)} пользователей'))
        
        self.stdout.write(f'Создание профилей...')
        self.create_profiles(users)
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {len(users)} профилей'))
        
        self.stdout.write(f'Создание {num_tags} тегов...')
        tags = self.create_tags(num_tags)
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {len(tags)} тегов'))
        
        self.stdout.write(f'Создание {num_questions} вопросов...')
        questions = self.create_questions(num_questions, users, tags)
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {len(questions)} вопросов'))
        
        self.stdout.write(f'Создание {num_answers} ответов...')
        answers = self.create_answers(num_answers, questions, users)
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {len(answers)} ответов'))
        
        self.stdout.write(f'Создание {num_likes} оценок...')
        self.create_likes(num_likes, questions, answers, users)
        self.stdout.write(self.style.SUCCESS(f'✓ Создано {num_likes} оценок'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ База данных успешно заполнена!'))
        self.stdout.write(f'Итого создано:')
        self.stdout.write(f'  - Пользователей: {num_users}')
        self.stdout.write(f'  - Тегов: {num_tags}')
        self.stdout.write(f'  - Вопросов: {num_questions}')
        self.stdout.write(f'  - Ответов: {num_answers}')
        self.stdout.write(f'  - Оценок: {num_likes}')

    def create_users(self, num_users):
        password_hash = make_password('password123')
        
        existing_usernames = set(
            User.objects.filter(username__startswith='user_')
            .values_list('username', flat=True)
        )
        
        users_to_create = []
        batch_size = 1000
        
        for i in range(0, num_users, batch_size):
            batch = []
            end = min(i + batch_size, num_users)
            
            for j in range(i, end):
                username = f'user_{j}'
                
                if username not in existing_usernames:
                    user = User(
                        username=username,
                        email=f'{username}@example.com',
                        password=password_hash,
                        date_joined=timezone.now() - timedelta(days=random.randint(0, 365)),
                        is_active=True,
                        is_staff=False,
                        is_superuser=False
                    )
                    batch.append(user)
            
            if batch:
                User.objects.bulk_create(batch, ignore_conflicts=True, batch_size=1000)
                users_to_create.extend(batch)
            
            if (i + batch_size) % 5000 == 0 or i + batch_size >= num_users:
                created_count = len(users_to_create)
                self.stdout.write(f'  Создано {created_count} новых пользователей...')
        
        all_users = list(User.objects.filter(username__startswith='user_').order_by('id')[:num_users])
        
        return all_users

    def create_profiles(self, users):
        if not users:
            return []
        
        user_ids = [u.id for u in users if u.id]
        if not user_ids:
            return []
        
        users_with_profiles = set(
            Profile.objects.filter(user_id__in=user_ids)
            .values_list('user_id', flat=True)
        )
        
        profiles_to_create = [
            Profile(user=user)
            for user in users
            if user.id and user.id not in users_with_profiles
        ]
        
        if profiles_to_create:
            batch_size = 1000
            for i in range(0, len(profiles_to_create), batch_size):
                batch = profiles_to_create[i:i + batch_size]
                Profile.objects.bulk_create(batch, ignore_conflicts=True)
        
        return profiles_to_create

    def create_tags(self, num_tags):
        tags = []
        batch_size = 1000
        
        tag_prefixes = ['python', 'django', 'javascript', 'react', 'vue', 'node', 'java', 'spring',
                        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'docker', 'kubernetes',
                        'aws', 'azure', 'gcp', 'linux', 'git', 'html', 'css', 'api', 'rest',
                        'graphql', 'microservices', 'devops', 'ci', 'cd', 'testing', 'pytest',
                        'unittest', 'selenium', 'performance', 'security', 'oauth', 'jwt', 'jwt',
                        'oauth2', 'websocket', 'grpc', 'tcp', 'http', 'https', 'ssl', 'tls']
        
        for i in range(0, num_tags, batch_size):
            batch = []
            end = min(i + batch_size, num_tags)
            
            for j in range(i, end):
                if j < len(tag_prefixes):
                    tag_name = tag_prefixes[j]
                else:
                    tag_name = f'tag_{j}'
                
                tag = Tag(name=tag_name)
                batch.append(tag)
            
            created_tags = Tag.objects.bulk_create(batch, ignore_conflicts=True)
            tags.extend(created_tags)
        
        return tags

    def create_questions(self, num_questions, users, tags):
        questions = []
        batch_size = 1000
        
        initial_max_id = Question.objects.aggregate(max_id=models.Max('id'))['max_id'] or 0
        titles = [
            'Как правильно настроить проект?',
            'В чем разница между X и Y?',
            'Как оптимизировать производительность?',
            'Как решить проблему с ошибкой?',
            'Какие best practices использовать?',
            'Как работает механизм X?',
            'Как правильно структурировать код?',
            'Как тестировать приложение?',
            'Как развернуть приложение?',
            'Как использовать библиотеку X?',
        ]
        
        texts = [
            'Я начинающий разработчик и хочу понять, как правильно настроить проект. Можете помочь?',
            'Недавно столкнулся с проблемой. Как лучше всего решить эту задачу?',
            'Хочу оптимизировать производительность моего приложения. С чего начать?',
            'Возникла ошибка при работе с базой данных. Как исправить?',
            'Какие best practices существуют для решения подобных задач?',
            'Интересует, как работает механизм под капотом. Можете объяснить?',
            'Как правильно организовать структуру проекта?',
            'Какие подходы к тестированию лучше использовать?',
            'Как правильно развернуть приложение в продакшн?',
            'Хочу использовать библиотеку, но не уверен в правильности подхода.',
        ]
        
        db_tags = list(Tag.objects.all()[:len(tags)]) if tags else []
        
        for i in range(0, num_questions, batch_size):
            batch = []
            end = min(i + batch_size, num_questions)
            
            for j in range(i, end):
                author = random.choice(users)
                title = f"{random.choice(titles)} #{j}"
                text = f"{random.choice(texts)} Вопрос номер {j}."
                created_at = timezone.now() - timedelta(days=random.randint(0, 365))
                
                question = Question(
                    title=title,
                    text=text,
                    author=author,
                    created_at=created_at
                )
                batch.append(question)
            
            Question.objects.bulk_create(batch)
            
            current_max_id = Question.objects.aggregate(max_id=models.Max('id'))['max_id'] or initial_max_id
            questions_with_tags = list(
                Question.objects.filter(id__gt=initial_max_id, id__lte=current_max_id)
                .select_related('author')
                .order_by('id')
            )
            initial_max_id = current_max_id
            
            questions.extend(questions_with_tags)
            
            if db_tags:
                for question in questions_with_tags:
                    num_tags_for_question = random.randint(1, min(5, len(db_tags)))
                    question_tags = random.sample(db_tags, num_tags_for_question)
                    question.tags.add(*question_tags)
            
            if (i + batch_size) % 10000 == 0 or i + batch_size >= num_questions:
                self.stdout.write(f'  Создано {len(questions)} вопросов...')
        
        return questions

    def create_answers(self, num_answers, questions, users):
        answers = []
        batch_size = 1000
        
        answer_texts = [
            'Отличный вопрос! Вот как можно решить эту проблему...',
            'Я сталкивался с подобной ситуацией. Рекомендую следующий подход...',
            'Для решения этой задачи можно использовать несколько методов...',
            'Попробуйте следующий способ, он должен помочь...',
            'Вот подробное объяснение с примерами кода...',
            'Это распространенная проблема. Решение заключается в...',
            'Могу предложить несколько вариантов решения...',
            'Вот пошаговая инструкция для решения задачи...',
            'Рекомендую использовать следующий подход...',
            'Это можно решить следующим образом...',
        ]
        
        for i in range(0, num_answers, batch_size):
            batch = []
            end = min(i + batch_size, num_answers)
            
            for j in range(i, end):
                question = random.choice(questions)
                author = random.choice(users)
                text = f"{random.choice(answer_texts)} Ответ номер {j}."
                is_correct = random.random() < 0.1
                days_since_question = (timezone.now() - question.created_at).days
                days_offset = random.randint(0, max(0, days_since_question))
                created_at = question.created_at + timedelta(days=days_offset)
                
                answer = Answer(
                    question=question,
                    author=author,
                    text=text,
                    is_correct=is_correct,
                    created_at=created_at
                )
                batch.append(answer)
            
            created_answers = Answer.objects.bulk_create(batch)
            answers.extend(created_answers)
            
            if (i + batch_size) % 10000 == 0 or i + batch_size >= num_answers:
                self.stdout.write(f'  Создано {len(answers)} ответов...')
        
        return answers

    def create_likes(self, num_likes, questions, answers, users):
        question_likes = []
        answer_likes = []
        batch_size = 1000
        
        num_question_likes = int(num_likes * 0.3)
        num_answer_likes = num_likes - num_question_likes
        
        self.stdout.write(f'  Создание {num_question_likes} оценок для вопросов...')
        question_likes_created = 0
        
        for i in range(0, num_question_likes, batch_size):
            batch = []
            end = min(i + batch_size, num_question_likes)
            
            for j in range(i, end):
                question = random.choice(questions)
                user = random.choice(users)
                is_positive = random.random() < 0.8
                days_since_question = (timezone.now() - question.created_at).days
                days_offset = random.randint(0, max(0, days_since_question))
                created_at = question.created_at + timedelta(days=days_offset)
                
                like = QuestionLike(
                    question=question,
                    user=user,
                    is_positive=is_positive,
                    created_at=created_at
                )
                batch.append(like)
            
            created = QuestionLike.objects.bulk_create(batch, ignore_conflicts=True)
            question_likes_created += len(created)
        
        self.stdout.write(f'  Создание {num_answer_likes} оценок для ответов...')
        answer_likes_created = 0
        
        for i in range(0, num_answer_likes, batch_size):
            batch = []
            end = min(i + batch_size, num_answer_likes)
            
            for j in range(i, end):
                answer = random.choice(answers)
                user = random.choice(users)
                is_positive = random.random() < 0.8
                days_since_answer = (timezone.now() - answer.created_at).days
                days_offset = random.randint(0, max(0, days_since_answer))
                created_at = answer.created_at + timedelta(days=days_offset)
                
                like = AnswerLike(
                    answer=answer,
                    user=user,
                    is_positive=is_positive,
                    created_at=created_at
                )
                batch.append(like)
            
            created = AnswerLike.objects.bulk_create(batch, ignore_conflicts=True)
            answer_likes_created += len(created)
        
        self.stdout.write(f'  ✓ Создано {question_likes_created} оценок для вопросов')
        self.stdout.write(f'  ✓ Создано {answer_likes_created} оценок для ответов')

