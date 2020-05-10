FROM python:3.6-slim

RUN apt-get update && \
    apt-get -y install git && \
    apt-get -y install build-essential && \
    pip install uwsgi && \
    apt-get purge -y build-essential && \
    apt -y autoremove

RUN ln -fs /usr/share/zoneinfo/Canada/Eastern /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

WORKDIR /app

ADD . /app

RUN pip install -r requirements-prod.txt

CMD ["uwsgi", "app.ini"]
