FROM python:3.7-alpine

LABEL Author="Christophe Lambin"
LABEL E-mail="christophe.lambin@gmail.com"
LABEL version="0.0.2"

RUN mkdir /app
WORKDIR /app

COPY *.py Pip* /app/

RUN apk update && \
    apk add gcc musl-dev

RUN pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --dev --system --deploy --ignore-pipfile

RUN pip install --no-cache-dir rpi.gpio

RUN rm -rf /var/cache/apk/*

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/python3", "pimon.py"]
CMD []
