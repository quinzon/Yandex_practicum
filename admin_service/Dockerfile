FROM python:3.11-slim

WORKDIR /opt/admin_service

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/opt

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

ENV TZ=Europe/Moscow
RUN apt-get install tzdata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input

ENTRYPOINT ["./entrypoint.sh"]