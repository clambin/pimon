ARG BASE_IMAGE=python:3.7-alpine
FROM $BASE_IMAGE
MAINTAINER Christophe Lambin <christophe.lambin@gmail.com>

RUN mkdir /app
WORKDIR /app

COPY *.py Pip* /app/
COPY metrics/*.py /app/metrics

RUN apk update && \
    apk --no-cache --virtual .build-deps add gcc musl-dev && \
    pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --dev --system --deploy --ignore-pipfile && \
    pip install --no-cache-dir rpi.gpio && \
    apk del .build-deps && \
    rm -rf /var/cache/apk/*

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/python3", "pimon.py"]
CMD []
