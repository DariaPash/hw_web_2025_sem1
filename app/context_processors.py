import logging
from django.db.models import Count, Q, F
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache import cache
from .models import Tag, Profile

logger = logging.getLogger(__name__)


def _parse_popular_tags(popular_tags_data):
    if not popular_tags_data or not isinstance(popular_tags_data, list):
        return []
    
    try:
        tag_ids = [
            tag.get('id') 
            for tag in popular_tags_data 
            if isinstance(tag, dict) and 'id' in tag
        ]
        
        if not tag_ids:
            return []
        
        tags_dict = {tag.id: tag for tag in Tag.objects.filter(id__in=tag_ids)}
        
        return [
            tags_dict[tag['id']] 
            for tag in popular_tags_data 
            if isinstance(tag, dict) and tag.get('id') in tags_dict
        ]
    except Exception as e:
        logger.error(f"Error loading popular tags: {e}")
        return []


def _parse_best_users(best_users_data):
    if not best_users_data or not isinstance(best_users_data, list):
        return []
    
    try:
        best_users = []
        for user_data in best_users_data:
            if isinstance(user_data, dict):
                best_users.append({
                    'username': user_data.get('username', ''),
                    'popularity': user_data.get('popularity', 0),
                    'reputation': user_data.get('reputation', 0),
                })
        return best_users
    except Exception as e:
        logger.error(f"Error loading best users: {e}")
        return []


def sidebar_context(request):
    try:
        popular_tags_data = cache.get('popular_tags', [])
        best_users_data = cache.get('best_users', [])
        
        popular_tags = _parse_popular_tags(popular_tags_data)
        best_users = _parse_best_users(best_users_data)
        
        return {
            'popular_tags': popular_tags,
            'best_users': best_users,
            'MEDIA_URL': settings.MEDIA_URL,
        }
    except Exception as e:
        logger.error(f"Critical error in sidebar_context: {e}")
        return {
            'popular_tags': [],
            'best_users': [],
            'MEDIA_URL': settings.MEDIA_URL,
        }