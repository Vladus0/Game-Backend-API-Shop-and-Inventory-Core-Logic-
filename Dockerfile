# Указываем базовый образ — официальный стабильный Python на Linux
FROM python:3.11-slim

# Устанавливаем рабочую папку внутри контейнера Linux
WORKDIR /app

# Копируем все файлы проекта (main.py, models.py, README.md) в контейнер
COPY . .

# Указываем команду для запуска нашего автономного Python-скрипта
CMD ["python", "main.py"]
