from django.contrib import admin
from .models import Profile, Question, Answer, Tag, QuestionLike, AnswerLike


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'get_username']
    search_fields = ['user__username', 'user__email', 'user_id']
    list_filter = ['user__date_joined']
    
    def get_username(self, obj):
        return obj.user.username if obj.user else '-'
    get_username.short_description = 'Username'
    get_username.admin_order_field = 'user__username'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'likes_cnt', 'dislikes_cnt', 'created_at']
    search_fields = ['title', 'text', 'author__username']
    list_filter = ['created_at', 'tags']
    filter_horizontal = ['tags']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'author', 'is_correct', 'likes_cnt', 'dislikes_cnt', 'created_at']
    search_fields = ['text', 'question__title', 'author__username']
    list_filter = ['is_correct', 'created_at']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'user', 'is_positive', 'created_at']
    search_fields = ['question__title', 'user__username']
    list_filter = ['is_positive', 'created_at']


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'answer', 'user', 'is_positive', 'created_at']
    search_fields = ['answer__text', 'user__username']
    list_filter = ['is_positive', 'created_at']


