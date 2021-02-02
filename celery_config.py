from celery.schedules import crontab


# CELERY_IMPORTS = ('app.tasks.test')
CELERY_TASK_RESULT_EXPIRES = 30
CELERY_TIMEZONE = 'UTC'

CELERY_ACCEPT_CONTENT = ['json', 'msgpack', 'yaml']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERYBEAT_SCHEDULE = {
    'test-celery': {
        'task': 'app.simple_periodic_task',
        # Every minute
        'schedule': crontab(minute="*"),
    },
    'every-five-minutes': {
        'task': 'app.every_2_min_repeating_task',
        # Every minute
        'schedule': crontab(minute="*/2"),
    },
}

CELERY_ROUTES = {
    'app.hello_world_on_a_different_queue_task': {'queue': 'queue2'}
}