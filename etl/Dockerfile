FROM --platform=linux/amd64 python:3.11-buster

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get -y dist-upgrade && apt install -y netcat

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

COPY . .

ENTRYPOINT ["bash", "start_etl.sh"]