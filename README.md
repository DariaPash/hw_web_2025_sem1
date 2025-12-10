# hw_web_2025_sem1


## Разворачивание и запуск проекта

### Установка и настройка

1. **Создайте и активируйте виртуальное окружение:**
```bash
python -m venv venv
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

2. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

3. **Настройте базу данных:**
```bash
python manage.py migrate
python manage.py fill_db n
```

### Запуск

```bash
python manage.py runserver
```
Сервер будет доступен по адресу: **http://127.0.0.1:8000/**

### Основные команды

- Создать миграции: `python manage.py makemigrations`
- Применить миграции: `python manage.py migrate`



