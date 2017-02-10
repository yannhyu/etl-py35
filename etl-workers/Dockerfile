FROM ubuntu:14.04

MAINTAINER Yann YU<yann.yu@medlytix.com>

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev
RUN apt-get install -y libpq-dev

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true


# copy source code
COPY . /etl-workers
WORKDIR /etl-workers

# install requirements
RUN pip install -r requirements.txt


# run the worker
#ENTRYPOINT ['celery']
#CMD ['-A','tasks', 'worker','--loglevel=info']
ENTRYPOINT celery -A celery_config worker --loglevel=info
