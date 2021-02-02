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
    hello_world_on_a_different_queue_task.delay('Deval for a different Queue!')
    return 'Hello, World!'

@app.route('/add/<int:a>/<int:b>', methods=['GET'])
def add_digits_route(a: int, b: int):
    task_handler_task.delay()
    print(f'got: a={a}, b={b}')
    get_sum_of_digits = lambda a, b: int(a) + int(b)
    sum_of_digits = get_sum_of_digits(a, b)
    return f"sum of {a} + {b} : {sum_of_digits}"

@app.route('/div/<int:a>/<int:b>', methods=['GET'])
def div_digits_route(a: int, b: int):
    print(f'got: a={a}, b={b}')
    divison_task.delay(a, b)
    return "Called divison task!"


# CELERY TASKS: #
# Task1: A normal celery task:
@celery_worker.task(name="app.simple_delay_task")
def delay_task(duration=10):
    print(f'Inside delay_task', f'time= {datetime.now()}')
    print(f"Delaying task for {duration} duration.")
    for i in range(duration):
        print(i + 1, "seconds")
        sleep(1)
    print('Delay completed!', datetime.now())
    return

# Task2: A Periodic Celery Task
@celery_worker.task(name='app.simple_periodic_task')
def simple_periodic_task(name: str = 'Deval'):
    print(f'Hey {name}, How you doin?')
    current_time = datetime.now()
    print(f'Task completed at time: {current_time}')

    
@celery_worker.task(name='app.every_2_min_repeating_task')
def every_2_min_repeating_task(name: str = 'Deval'):
    print(f'Hey {name}, How you doin?', "let's meet after 2 min :)")
    current_time = datetime.now()
    print(f'Task completed at time: {current_time}')

    
# Task3: Calling Task with Task
@celery_worker.task(name='app.task_handler')
def task_handler_task():
    print("Inside task_handler -> calling: delay_task")
    delay_task.s().delay(duration=4)
    print("Completed delay_task, now back to task_handler")

# Task4: Different ways of executing a task in celery:
@app.route('/greet/<name>/<int:delay>', methods=['GET'])
@app.route('/greet/<name>/', methods=['GET'])
def greetings_route_with_different_methods(name, delay: int = 0):
    print(f'Inside', greetings_route_with_different_methods.__name__)
    print(f'Current time: ', datetime.now())
    if delay == 0:
        delay_task.delay()
    else:
        print(f'Now applying apply_async and it will be starting after countdown of {delay} seconds.')
        delay_task.apply_async((delay,), countdown=delay)
        
    return f'Hey {name}, How you doing?'

# Task5: Adding task on a different queue:
# cmd: celery -A app.celery_worker -l INFO -Q celery,queue2
@celery_worker.task(name='app.hello_world_on_a_different_queue_task')
def hello_world_on_a_different_queue_task(name: str):
    print(f'Hello', name)
    
# Task7: Retry task:
@celery_worker.task(bind=True, name='app.divison_task')
def divison_task(self, a: int, b: int):
    print('Inside', divison_task.__name__)
    print('for', dict(a=a, b=b))
    try:
        quotient = a / b
        return quotient
    except ZeroDivisionError as exc:
        print('ZeroDivisonError occured for: ', dict(a=a, b=b))
        print('Now incrementing b')
        b += 1
        raise self.retry(exc = exc, countdown=3, max_retries=5)
    except Exception as e:
        print('Got another excpetion', 'now incrementing b', dict(a=a, b=b))
        divison_task.s().delay(a, b + 1)