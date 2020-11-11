from celery import shared_task
#TODO: can probably remove this if unneeded
@shared_task
def simple_task():
    print("The sample task just ran FROM RDB folder", flush=True)

