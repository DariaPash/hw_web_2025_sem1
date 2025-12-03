# hw_web_2025_sem1

## Разворачивание и запуск проекта

### Установка зависимостей

1. Создайте виртуальное окружение (рекомендуется):
```bash
python -m venv venv
```

2. Активируйте виртуальное окружение:
   - На macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
   - На Windows:
   ```bash
   venv\Scripts\activate
   ```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

### Настройка базы данных

1. Примените миграции:
```bash
python manage.py migrate
```

2. (Опционально) Создайте суперпользователя для доступа к админ-панели:
```bash
python manage.py createsuperuser
```

### Запуск проекта

1. Запустите сервер разработки:
```bash
python manage.py runserver
```

2. Откройте браузер и перейдите по адресу:
```
http://127.0.0.1:8000/
```

### Дополнительные команды

- Сбор статических файлов (для production):
```bash
python manage.py collectstatic
```

- Создание новых миграций после изменения моделей:
```bash
python manage.py makemigrations
```