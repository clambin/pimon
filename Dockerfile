FROM multiarch/qemu-user-static:x86_64-arm as qemu
FROM arm32v7/python:3.7-alpine
MAINTAINER Christophe Lambin <christophe.lambin@gmail.com>

COPY --from=qemu /usr/bin/qemu-arm-static /usr/bin

RUN mkdir /app
WORKDIR /app

COPY *.py Pip* ./
COPY metrics/*.py metrics/

RUN apk update && \
    apk --no-cache --virtual .build-deps add gcc musl-dev && \
    pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --system --deploy --ignore-pipfile && \
    pip install --no-cache-dir rpi.gpio && \
    apk del .build-deps && \
    rm -rf /var/cache/apk/*

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/python3", "pimon.py"]
CMD []
