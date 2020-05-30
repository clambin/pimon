FROM multiarch/qemu-user-static:x86_64-arm as qemu
FROM arm32v7/python:3.7-alpine as builder

COPY --from=qemu /usr/bin/qemu-arm-static /usr/bin

RUN apk update && \
    apk --no-cache add gcc musl-dev && \
    pip install --upgrade pip && \
    pip install --no-cache-dir rpi.gpio

FROM arm32v7/python:3.7-alpine
MAINTAINER Christophe Lambin <christophe.lambin@gmail.com>

COPY --from=qemu /usr/bin/qemu-arm-static /usr/bin
COPY --from=builder /usr/local/lib/python3.7/site-packages/RPi /usr/local/lib/python3.7/site-packages/RPi

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install pipenv

COPY Pip* ./

RUN pipenv install --system --deploy --ignore-pipfile

COPY pimon.py ./
COPY libpimon/*.py libpimon/

EXPOSE 8080

ENTRYPOINT ["/usr/local/bin/python3", "pimon.py"]
CMD []
