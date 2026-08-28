FROM jenkins/jenkins:lts-jdk17

USER root

ARG DOCKER_COMPOSE_VERSION=v2.27.0

RUN apt-get update \
    && apt-get install -y \
        python3 \
        python3-venv \
        python3-pip \
        git \
        docker.io \
        curl \
        ca-certificates \
    && mkdir -p /usr/local/lib/docker/cli-plugins \
    && curl -fL "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-linux-x86_64" \
        -o /usr/local/lib/docker/cli-plugins/docker-compose \
    && chmod +x /usr/local/lib/docker/cli-plugins/docker-compose \
    && rm -rf /var/lib/apt/lists/*

USER jenkins
