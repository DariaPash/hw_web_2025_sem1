from django.db.models import Count, Q, F
from django.contrib.auth.models import User
from django.conf import settings
from .models import Tag, Profile


def sidebar_context(request):
    """
    Context processor для aside-блока.
    Возвращает популярные теги и лучших участников из БД.
    """
    # Константы репутации
    REPUTATION_QUESTION = Profile.REPUTATION_QUESTION
    REPUTATION_ANSWER = Profile.REPUTATION_ANSWER
    REPUTATION_ACCEPTED_ANSWER = Profile.REPUTATION_ACCEPTED_ANSWER
    
    # Получаем топ-10 популярных тегов по количеству вопросов
    popular_tags = Tag.objects.annotate(
        questions_count=Count('questions')
    ).order_by('-questions_count')[:10]
    
    # Получаем лучших участников по репутации
    # Вычисляем репутацию через аннотации в БД
    best_users_queryset = User.objects.annotate(
        questions_count=Count('questions', distinct=True),
        answers_count=Count('answers', distinct=True),
        accepted_answers=Count('answers', filter=Q(answers__is_correct=True), distinct=True),
        reputation=(
            F('questions_count') * REPUTATION_QUESTION +
            F('answers_count') * REPUTATION_ANSWER +
            F('accepted_answers') * REPUTATION_ACCEPTED_ANSWER
        )
    ).filter(
        reputation__gt=0  # Только пользователи с репутацией > 0
    ).order_by('-reputation')[:5]
    
    # Преобразуем в список словарей для шаблона
    best_users = [
        {
            'username': user.username,
            'reputation': user.reputation,
        }
        for user in best_users_queryset
    ]
    
    return {
        'popular_tags': popular_tags,
        'best_users': best_users,
        'MEDIA_URL': settings.MEDIA_URL,
    }

