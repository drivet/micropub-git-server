FROM tiangolo/uwsgi-nginx:python3.7

WORKDIR /app

ADD . /app

ENV MICROPUB_ROOT=/var/local/micropub

RUN pip install -r requirements-prod.txt
