from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import F
from .models import QuestionLike, AnswerLike, Question, Answer


@receiver(post_save, sender=QuestionLike)
def update_question_likes_count_on_save(sender, instance, created, **kwargs):
    """
    Обновляет счетчики likes_cnt и dislikes_cnt для вопроса
    при создании или изменении лайка.
    """
    question = instance.question
    
    if created:
        # Новый лайк - увеличиваем соответствующий счетчик
        if instance.is_positive:
            Question.objects.filter(id=question.id).update(likes_cnt=F('likes_cnt') + 1)
        else:
            Question.objects.filter(id=question.id).update(dislikes_cnt=F('dislikes_cnt') + 1)
    else:
        # Изменение существующего лайка - пересчитываем оба счетчика
        question.likes_cnt = QuestionLike.objects.filter(
            question=question, 
            is_positive=True
        ).count()
        question.dislikes_cnt = QuestionLike.objects.filter(
            question=question, 
            is_positive=False
        ).count()
        question.save(update_fields=['likes_cnt', 'dislikes_cnt'])


@receiver(post_delete, sender=QuestionLike)
def update_question_likes_count_on_delete(sender, instance, **kwargs):
    """
    Обновляет счетчики likes_cnt и dislikes_cnt для вопроса
    при удалении лайка.
    """
    question = instance.question
    
    # Уменьшаем соответствующий счетчик
    if instance.is_positive:
        Question.objects.filter(id=question.id).update(likes_cnt=F('likes_cnt') - 1)
    else:
        Question.objects.filter(id=question.id).update(dislikes_cnt=F('dislikes_cnt') - 1)


@receiver(post_save, sender=AnswerLike)
def update_answer_likes_count_on_save(sender, instance, created, **kwargs):
    """
    Обновляет счетчики likes_cnt и dislikes_cnt для ответа
    при создании или изменении лайка.
    """
    answer = instance.answer
    
    if created:
        # Новый лайк - увеличиваем соответствующий счетчик
        if instance.is_positive:
            Answer.objects.filter(id=answer.id).update(likes_cnt=F('likes_cnt') + 1)
        else:
            Answer.objects.filter(id=answer.id).update(dislikes_cnt=F('dislikes_cnt') + 1)
    else:
        # Изменение существующего лайка - пересчитываем оба счетчика
        answer.likes_cnt = AnswerLike.objects.filter(
            answer=answer, 
            is_positive=True
        ).count()
        answer.dislikes_cnt = AnswerLike.objects.filter(
            answer=answer, 
            is_positive=False
        ).count()
        answer.save(update_fields=['likes_cnt', 'dislikes_cnt'])


@receiver(post_delete, sender=AnswerLike)
def update_answer_likes_count_on_delete(sender, instance, **kwargs):
    """
    Обновляет счетчики likes_cnt и dislikes_cnt для ответа
    при удалении лайка.
    """
    answer = instance.answer
    
    # Уменьшаем соответствующий счетчик
    if instance.is_positive:
        Answer.objects.filter(id=answer.id).update(likes_cnt=F('likes_cnt') - 1)
    else:
        Answer.objects.filter(id=answer.id).update(dislikes_cnt=F('dislikes_cnt') - 1)

