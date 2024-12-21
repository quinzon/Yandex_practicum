FROM --platform=linux/amd64 python:3.12.1

WORKDIR /opt/app/bigdata_etl

RUN apt-get update \
    && apt-get install -y procps="2:4.0.2-3" \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . .

RUN chmod +x ./main.py

RUN groupadd -r app_group \
    && useradd -d /opt/app -r -g app_group app \
    && chown app:app_group -R /opt/app/ \
    && chown app:app_group -R /var/log/

USER app

ENTRYPOINT ["python", "/opt/app/bigdata_etl/main.py"]
