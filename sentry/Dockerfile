FROM python:3.11-slim

WORKDIR /opt/sentry

# Копируем всю папку в контейнер
COPY . .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Указываем скрипт для выполнения
CMD ["python", "sentry_client.py"]
