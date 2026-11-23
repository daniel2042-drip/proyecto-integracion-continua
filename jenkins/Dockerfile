# Uso académico LOCAL. El montaje del socket Docker en compose otorga privilegios elevados.
FROM jenkins/jenkins:lts-jdk21
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io git ca-certificates openssl \
    && rm -rf /var/lib/apt/lists/*
USER jenkins
RUN jenkins-plugin-cli --plugins workflow-aggregator git junit
