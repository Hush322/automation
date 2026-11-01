FROM jenkins/ssh-agent

USER root

RUN apt-get update && \
    apt-get install -y \
    php-cli \
    php-phpdbg \
    php-xml \
    php-curl \
    php-mbstring \
    curl \
    unzip \
    git && \
    rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/local/bin/composer
