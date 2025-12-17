#!/usr/bin/env python3
"""
Скрипт для тестирования отправки сообщений в Centrifugo
Использование: python test_centrifugo.py <question_id> [text]
"""
import sys
import os
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'askdi.settings')
django.setup()

from app.centrifugo_client import publish_to_centrifugo
from app.models import Question, Answer, User
from django.utils import timezone


def send_test_answer(question_id, text=None):
    """Отправляет тестовый ответ в Centrifugo"""
    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        print(f"Вопрос с ID {question_id} не найден")
        return False
    
    user = User.objects.first()
    if not user:
        print("Нет пользователей в базе данных")
        return False
    
    if text is None:
        text = f"Тестовый ответ отправлен в {timezone.now().strftime('%H:%M:%S')}"
    
    answer = Answer.objects.create(
        question=question,
        author=user,
        text=text,
        likes_cnt=0,
        dislikes_cnt=0,
    )
    
    print(f"Создан ответ ID: {answer.id}")
    
    channel = f"question:{question_id}"
    answer_data = {
        'id': answer.id,
        'text': answer.text,
        'author': {
            'id': answer.author.id,
            'username': answer.author.username,
        },
        'is_correct': answer.is_correct,
        'likes_cnt': answer.likes_cnt,
        'dislikes_cnt': answer.dislikes_cnt,
        'created_at': answer.created_at.isoformat(),
        'time_ago': answer.get_time_ago(),
    }
    
    print(f"Отправка сообщения в канал: {channel}")
    print(f"Текст: {text[:50]}...")
    
    success = publish_to_centrifugo(channel, answer_data)
    
    if success:
        print(f"Сообщение успешно отправлено в Centrifugo!")
        print(f"Откройте страницу вопроса: http://localhost:8000/question/{question_id}/")
        print(f"Ответ должен появиться автоматически без перезагрузки страницы")
        return True
    else:
        print(f"Ошибка при отправке сообщения в Centrifugo")
        print(f"Убедитесь, что Centrifugo запущен на порту 8001")
        return False


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python test_centrifugo.py <question_id> [text]")
        print("\nПримеры:")
        print("  python test_centrifugo.py 1")
        print("  python test_centrifugo.py 1 'Мой тестовый ответ'")
        sys.exit(1)
    
    question_id = int(sys.argv[1])
    text = sys.argv[2] if len(sys.argv) > 2 else None
    
    send_test_answer(question_id, text)
