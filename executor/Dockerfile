
FROM ubuntu:18.04

ENV LANGUAGE=de_DE LANG=de_DE.utf8 LC_ALL=de_DE.utf8 DEBIAN_FRONTEND=noninteractive PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y apt-utils locales python3 python3-pip cron gcc make autoconf curl default-jdk nano git \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i de_DE -c -f UTF-8 -A /usr/share/locale/locale.alias de_DE.UTF-8


COPY requirements.txt /
RUN pip3 install --no-cache-dir -r /requirements.txt

COPY dist/*.whl /
RUN pip3 install /*.whl

RUN chmod -R o-x /usr/local/sbin \
&& chmod -R o-x /usr/local/bin \
&& chmod -R o-x /usr/sbin \
&& chmod -R o-x /usr/bin \
&& chmod -R o-x /sbin \
&& chmod -R o-x /bin \
&& chmod -R o+x /bin/bash \
&& chmod o+x /bin

RUN adduser --gecos "" --disabled-password opensubmit


RUN touch /var/log/cron.log
# Redirect output directly into Docker stdout / stderr
RUN echo "* * * * * /usr/local/bin/opensubmit-exec run > /proc/1/fd/1 2>/proc/1/fd/2\n" | crontab

COPY docker/docker-entry.sh /
RUN chmod 700 /docker-entry.sh

ENTRYPOINT ["/docker-entry.sh"]
