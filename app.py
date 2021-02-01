from flask import Flask
from celery_importer import make_celery
from time import sleep
from datetime import datetime

app = Flask(__name__)
backend='rpc://'
broker='pyamqp://'
app.config.update(
    # CELERY_BROKER_URL='amqp://localhost:15672',
    # CELERY_RESULT_BACKEND='rpc://'
    
    # TEST:
    CELERY_BROKER_URL = broker,
    CELERY_RESULT_BACKEND = backend
)
celery_worker = make_celery(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/add/<a>/<b>', methods=['GET'])
def add_digits_route(a, b):
    delay_task.delay()
    print(f'got: a={a}, b={b}')
    get_sum_of_digits = lambda a, b: int(a) + int(b)
    sum_of_digits = get_sum_of_digits(a, b)
    return f"sum of {a} + {b} : {sum_of_digits}"


# CELERY TASKS: #
# Task1: A normal celery task:
@celery_worker.task(name="app.simple_delay_task")
def delay_task(duration=10):
    print(f"Delaying task for {duration} duration.")
    for i in range(duration):
        print(i + 1, "seconds")
        sleep(1)
    print('Delay completed!')
    return

# Task2: A Periodic Celery Task
@celery_worker.task(name='app.simple_periodic_task')
def simple_periodic_task(name: str = 'Deval'):
    print(f'Hey {name}, How you doin?')
    current_time = datetime.now()
    print(f'Task completed at time: {current_time}')