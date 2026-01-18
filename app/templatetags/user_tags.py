from django import template
from django.contrib.staticfiles.storage import staticfiles_storage

register = template.Library()


@register.simple_tag
def user_avatar_url(user):
    """Возвращает URL аватара пользователя или дефолтный аватар"""
    if user and hasattr(user, 'profile'):
        try:
            profile = user.profile
            if profile and profile.avatar:
                return profile.avatar.url
        except:
            pass
    # Дефолтный аватар
    try:
        return staticfiles_storage.url('img/default-avatar.png')
    except:
        return '/static/img/default-avatar.png'


@register.simple_tag
def user_display_name(user):
    """Возвращает отображаемое имя пользователя (first_name или username)"""
    if user:
        return user.first_name if user.first_name else user.username
    return ''
