# Используем Python 3.11
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /opt/links_shortener

ENV PYTHONPATH=/opt/links_shortener/app

# Копируем всё содержимое папки links_shortener в контейнер
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт
EXPOSE 8001

# Указываем команду запуска
CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=8001"]
