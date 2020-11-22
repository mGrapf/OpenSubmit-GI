
FROM ubuntu:18.04

ENV LANGUAGE=de_DE LANG=de_DE.utf8 LC_ALL=de_DE.utf8 DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y locales python3 python3-pip cron gcc make autoconf curl default-jdk nano \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8


COPY requirements.txt /
RUN pip3 install --no-cache-dir -r /requirements.txt

COPY dist/*.whl /
RUN pip3 install /*.whl

COPY docker/docker-entry.sh /
RUN chmod 777 /docker-entry.sh

RUN adduser --gecos "" --disabled-password --uid 1001 opensubmit
USER 1001:1001

ENTRYPOINT ["/docker-entry.sh"]
