"""
Management команда для обновления кэша популярных тегов и лучших пользователей.
Должна запускаться через cron.
"""
from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.db.models import Count, Q, F, Sum
from django.utils import timezone
from datetime import timedelta
from app.models import Tag, Question, Answer, User
from app.models import Profile


class Command(BaseCommand):
    help = 'Обновляет кэш популярных тегов и лучших пользователей'

    def handle(self, *args, **options):
        self.stdout.write('Обновление кэша популярных тегов и лучших пользователей...')
        
        # Обновляем популярные теги
        self.update_popular_tags()
        
        # Обновляем лучших пользователей
        self.update_best_users()
        
        self.stdout.write(self.style.SUCCESS('Кэш успешно обновлен!'))

    def update_popular_tags(self):
        """Обновляет кэш популярных тегов за последние 3 месяца"""
        three_months_ago = timezone.now() - timedelta(days=90)
        
        # Получаем топ-10 тегов с наибольшим количеством вопросов за последние 3 месяца
        popular_tags = Tag.objects.filter(
            questions__created_at__gte=three_months_ago
        ).annotate(
            questions_count=Count('questions', filter=Q(questions__created_at__gte=three_months_ago))
        ).filter(
            questions_count__gt=0
        ).order_by('-questions_count')[:10]
        
        # Сохраняем в кэш
        tags_data = [
            {
                'id': tag.id,
                'name': tag.name,
                'questions_count': tag.questions_count,
            }
            for tag in popular_tags
        ]
        
        cache.set('popular_tags', tags_data, timeout=None)  # Без таймаута, обновляется через cron
        self.stdout.write(f'Обновлено {len(tags_data)} популярных тегов')

    def update_best_users(self):
        """Обновляет кэш лучших пользователей за последнюю неделю"""
        one_week_ago = timezone.now() - timedelta(days=7)
        
        # Константы репутации
        REPUTATION_QUESTION = Profile.REPUTATION_QUESTION
        REPUTATION_ANSWER = Profile.REPUTATION_ANSWER
        REPUTATION_ACCEPTED_ANSWER = Profile.REPUTATION_ACCEPTED_ANSWER
        
        # Получаем пользователей с вопросами или ответами за последнюю неделю
        # Вычисляем популярность на основе лайков вопросов и ответов
        best_users = User.objects.filter(
            Q(questions__created_at__gte=one_week_ago) | 
            Q(answers__created_at__gte=one_week_ago)
        ).annotate(
            # Количество вопросов за неделю
            recent_questions_count=Count('questions', filter=Q(questions__created_at__gte=one_week_ago), distinct=True),
            # Количество ответов за неделю
            recent_answers_count=Count('answers', filter=Q(answers__created_at__gte=one_week_ago), distinct=True),
            # Сумма лайков вопросов за неделю
            questions_likes=Sum('questions__likes_cnt', filter=Q(questions__created_at__gte=one_week_ago)),
            # Сумма лайков ответов за неделю
            answers_likes=Sum('answers__likes_cnt', filter=Q(answers__created_at__gte=one_week_ago)),
            # Количество принятых ответов за неделю
            accepted_answers=Count('answers', filter=Q(answers__is_correct=True, answers__created_at__gte=one_week_ago), distinct=True),
        ).filter(
            Q(recent_questions_count__gt=0) | Q(recent_answers_count__gt=0)
        )
        
        # Вычисляем популярность для каждого пользователя
        users_with_popularity = []
        for user in best_users:
            # Популярность = сумма лайков вопросов + сумма лайков ответов + бонус за принятые ответы
            popularity = (
                (user.questions_likes or 0) +
                (user.answers_likes or 0) +
                (user.accepted_answers or 0) * 10
            )
            
            if popularity > 0:
                users_with_popularity.append({
                    'user': user,
                    'popularity': popularity,
                })
        
        # Сортируем по популярности и берем топ-10
        users_with_popularity.sort(key=lambda x: x['popularity'], reverse=True)
        top_users = users_with_popularity[:10]
        
        # Сохраняем в кэш
        users_data = [
            {
                'id': item['user'].id,
                'username': item['user'].username,
                'popularity': item['popularity'],
            }
            for item in top_users
        ]
        
        cache.set('best_users', users_data, timeout=None)  # Без таймаута, обновляется через cron
        self.stdout.write(f'Обновлено {len(users_data)} лучших пользователей')
