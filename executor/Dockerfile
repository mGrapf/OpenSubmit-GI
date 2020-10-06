
FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive \
	PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y locales python3 python3-pip cron gcc make autoconf curl default-jdk nano \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY dist/*.whl /
RUN pip3 install /*.whl

COPY docker/docker-entry.sh /
RUN chmod 777 /docker-entry.sh
ENTRYPOINT ["/docker-entry.sh"]
