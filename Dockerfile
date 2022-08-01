FROM python:3.11-rc-alpine
ENV LANG C.UTF-8

RUN mkdir /votingapp

RUN apk update
RUN apk add postgresql-dev postgresql-client gcc  musl-dev

ADD requirements.txt /votingapp/requirements.txt
RUN pip install -r /votingapp/requirements.txt

WORKDIR /votingapp

EXPOSE 8000

CMD gunicorn -b :8000 django.wsgi
