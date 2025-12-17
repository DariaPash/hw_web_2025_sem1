from django.db.models import Count, Q, F
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache
from .models import Tag, Profile


def sidebar_context(request):
    """
    Context processor для aside-блока.
    Возвращает популярные теги и лучших участников из кэша.
    Если кэш пуст, возвращает пустые списки (данные должны обновляться через cron).
    """
    try:
        popular_tags_data = cache.get('popular_tags', [])
        
        popular_tags = []
        if popular_tags_data and isinstance(popular_tags_data, list):
            try:
                tag_ids = [tag.get('id') for tag in popular_tags_data if isinstance(tag, dict) and 'id' in tag]
                if tag_ids:
                    tags_dict = {tag.id: tag for tag in Tag.objects.filter(id__in=tag_ids)}
                    popular_tags = [tags_dict[tag['id']] for tag in popular_tags_data 
                                   if isinstance(tag, dict) and tag.get('id') in tags_dict]
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error loading popular tags: {e}")
                popular_tags = []
        
        best_users_data = cache.get('best_users', [])
        
        best_users = []
        if best_users_data and isinstance(best_users_data, list):
            try:
                for user_data in best_users_data:
                    if isinstance(user_data, dict):
                        best_users.append({
                            'username': user_data.get('username', ''),
                            'popularity': user_data.get('popularity', 0),
                            'reputation': user_data.get('reputation', 0),
                        })
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error loading best users: {e}")
                best_users = []
        
        return {
            'popular_tags': popular_tags,
            'best_users': best_users,
            'MEDIA_URL': settings.MEDIA_URL,
        }
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Critical error in sidebar_context: {e}")
        return {
            'popular_tags': [],
            'best_users': [],
            'MEDIA_URL': settings.MEDIA_URL,
        }

