from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from django.utils.timesince import timesince


class QuestionManager(models.Manager):
    
    def new(self):
        return self.get_queryset().order_by('-created_at')
    
    def best(self):
        from django.db.models import F
        return self.get_queryset().annotate(
            rating=F('likes_cnt') - F('dislikes_cnt')
        ).order_by('-rating', '-created_at')
    
    def by_tag(self, tag_name):
        return self.get_queryset().filter(tags__name=tag_name).distinct()
    
    def by_author(self, username):
        return self.get_queryset().filter(author__username=username)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название тега')
    
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Question(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст вопроса')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='questions', verbose_name='Автор')
    tags = models.ManyToManyField(Tag, related_name='questions', verbose_name='Теги')
    likes_cnt = models.IntegerField(default=0, verbose_name='Количество лайков')
    dislikes_cnt = models.IntegerField(default=0, verbose_name='Количество дизлайков')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    objects = QuestionManager()
    
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return self.title
    
    def get_rating(self):
        return self.likes_cnt - self.dislikes_cnt
    
    def get_answers_count(self):
        return self.answers.count()
    
    def get_url(self):
        return reverse('question', kwargs={'question_id': self.id})
    
    def get_preview(self, length=200):
        if len(self.text) <= length:
            return self.text
        return self.text[:length] + '...'
    
    def get_time_ago(self):
        return timesince(self.created_at)
    
    @property
    def votes_up(self):
        return self.likes_cnt
    
    @property
    def votes_down(self):
        return self.dislikes_cnt
    
    @property
    def preview(self):
        return self.get_preview()
    
    @property
    def author_name(self):
        return self.author.username if self.author else 'Удаленный пользователь'
    
    @property
    def time_ago(self):
        return self.get_time_ago()
    
    @property
    def answers_count(self):
        return self.get_answers_count()


class Answer(models.Model):
    text = models.TextField(verbose_name='Текст ответа')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name='Вопрос')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', verbose_name='Автор')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')
    likes_cnt = models.IntegerField(default=0, verbose_name='Количество лайков')
    dislikes_cnt = models.IntegerField(default=0, verbose_name='Количество дизлайков')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-is_correct', '-created_at']
        indexes = [
            models.Index(fields=['question', '-created_at']),
            models.Index(fields=['author']),
        ]
    
    def __str__(self):
        return f"Ответ на: {self.question.title[:50]}"
    
    def get_rating(self):
        return self.likes_cnt - self.dislikes_cnt
    
    def get_time_ago(self):
        return timesince(self.created_at)
    
    def get_question_url(self):
        return self.question.get_url()
    
    @property
    def votes_up(self):
        return self.likes_cnt
    
    @property
    def votes_down(self):
        return self.dislikes_cnt
    
    @property
    def author_name(self):
        return self.author.username
    
    @property
    def time_ago(self):
        return self.get_time_ago()


class Profile(models.Model):
    # Коэффициенты репутации
    REPUTATION_QUESTION = 5
    REPUTATION_ANSWER = 3
    REPUTATION_ACCEPTED_ANSWER = 10
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='Пользователь')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
    
    def __str__(self):
        return f"Профиль #{self.user_id}"
    
    def get_stats(self):
        questions_count = self.user.questions.count()
        answers_count = self.user.answers.count()
        accepted_answers = self.user.answers.filter(is_correct=True).count()
        reputation = (questions_count * self.REPUTATION_QUESTION + 
                     answers_count * self.REPUTATION_ANSWER + 
                     accepted_answers * self.REPUTATION_ACCEPTED_ANSWER)
        return {
            'reputation': reputation,
            'questions_count': questions_count,
            'answers_count': answers_count,
            'accepted_answers': accepted_answers,
        }


class QuestionLike(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    is_positive = models.BooleanField(default=True, verbose_name='Лайк (True) или дизлайк (False)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Лайк вопроса'
        verbose_name_plural = 'Лайки вопросов'
        unique_together = [['question', 'user']]
        indexes = [
            models.Index(fields=['question', 'user']),
        ]
    
    def __str__(self):
        like_type = 'лайк' if self.is_positive else 'дизлайк'
        return f"{like_type} на вопрос #{self.question_id} от пользователя #{self.user_id}"


class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name='Ответ')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    is_positive = models.BooleanField(default=True, verbose_name='Лайк (True) или дизлайк (False)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Лайк ответа'
        verbose_name_plural = 'Лайки ответов'
        unique_together = [['answer', 'user']]
        indexes = [
            models.Index(fields=['answer', 'user']),
        ]
    
    def __str__(self):
        like_type = 'лайк' if self.is_positive else 'дизлайк'
        return f"{like_type} на ответ #{self.answer_id} от пользователя #{self.user_id}"
