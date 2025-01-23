# Используем Python 3.11
FROM python:3.11-slim


WORKDIR /opt/links_shortener

ENV PYTHONPATH=/opt/links_shortener/app


COPY . .


RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8001


CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=8001"]
