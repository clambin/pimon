FROM python:3.7-alpine

LABEL Author="Christophe Lambin"
LABEL E-mail="christophe.lambin@gmail.com"
LABEL version="0.2"

RUN mkdir /app
WORKDIR /app

COPY *.py freq temp Pip* /app/

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
