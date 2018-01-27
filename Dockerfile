FROM python:3.6.4-alpine
LABEL maintainer="r.tomjaks@gmail.com"

ENV PYTHONUNBUFFERED 1

ENV DOCKER_VERSION 17.12.0-ce

WORKDIR /usr/src/app

RUN apk --no-cache add curl \
    && curl -sSL -O https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_VERSION}.tgz \
    && tar zxf docker-${DOCKER_VERSION}.tgz \
    && mv $(find -name 'docker' -type f) /usr/local/bin/ \
    && chmod +x /usr/local/bin/docker \
    && rm -rf docker*

COPY main.py docker-gc

ENTRYPOINT ["python", "docker-gc"]

CMD ["--help"]
