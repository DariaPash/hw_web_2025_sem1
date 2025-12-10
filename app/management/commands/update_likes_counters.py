from django.core.management.base import BaseCommand
from app.models import Question, Answer, QuestionLike, AnswerLike
from django.db.models import Count, Q


class Command(BaseCommand):
    help = 'Обновляет счетчики likes_cnt и dislikes_cnt для всех вопросов и ответов'

    def handle(self, *args, **options):
        self.stdout.write('Обновление счетчиков лайков для вопросов...')
        
        # Обновляем счетчики для вопросов
        questions = Question.objects.all()
        for q in questions:
            q.likes_cnt = QuestionLike.objects.filter(question=q, is_positive=True).count()
            q.dislikes_cnt = QuestionLike.objects.filter(question=q, is_positive=False).count()
            q.save(update_fields=['likes_cnt', 'dislikes_cnt'])
        
        self.stdout.write(self.style.SUCCESS(f'✓ Обновлено {questions.count()} вопросов'))
        
        self.stdout.write('Обновление счетчиков лайков для ответов...')
        
        # Обновляем счетчики для ответов
        answers = Answer.objects.all()
        for a in answers:
            a.likes_cnt = AnswerLike.objects.filter(answer=a, is_positive=True).count()
            a.dislikes_cnt = AnswerLike.objects.filter(answer=a, is_positive=False).count()
            a.save(update_fields=['likes_cnt', 'dislikes_cnt'])
        
        self.stdout.write(self.style.SUCCESS(f'✓ Обновлено {answers.count()} ответов'))
        self.stdout.write(self.style.SUCCESS('\n✓ Все счетчики обновлены!'))


