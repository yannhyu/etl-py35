import os
from celery import Celery

env=os.environ
CELERY_BROKER_URL=env.get('CELERY_BROKER_URL','redis://localhost:6379'),
CELERY_RESULT_BACKEND=env.get('CELERY_RESULT_BACKEND','redis://localhost:6379')


celery= Celery('celery_config',
                broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND,
                include=['ins00.add', 'ins00.read_db_data'])
