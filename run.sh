#!/bin/bash
#красивая обертка над manage.py

source myenv/bin/activate

# Если команда - runserver, сначала убиваем процесс на порту
if [ "$1" = "runserver" ]; then
    # Определяем порт (по умолчанию 8000)
    PORT=8000
    if [ -n "$2" ]; then
        # Если порт указан как 0.0.0.0:8000 или 127.0.0.1:8000
        if [[ "$2" =~ :([0-9]+)$ ]]; then
            PORT="${BASH_REMATCH[1]}"
        elif [[ "$2" =~ ^[0-9]+$ ]]; then
            PORT="$2"
        fi
    fi
    
    # Ищем и убиваем процесс на порту
    PID=$(lsof -ti:$PORT 2>/dev/null)
    if [ -n "$PID" ]; then
        echo "Найден процесс на порту $PORT (PID: $PID), завершаю..."
        kill -9 $PID 2>/dev/null
        sleep 1
    fi
fi

python manage.py "$@"

