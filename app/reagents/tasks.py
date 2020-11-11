from celery import shared_task
from .models import Reagent, ReagentDelta, PADelta, AutoStainerStation

@shared_task
def simple_task():
    print("The sample task just ran from folder with models ;)", flush=True)

@shared_task
def check_and_remove_PADeltas():
    # remove all deltas older than the earliest Autostainer sycn timestamp
    print("Removing older PA delta files...", flush=True)
    autostainer = AutoStainerStation.objects.earliest('latest_sync_time_PA')
    deltas = PADelta.objects.filter(date__lte=autostainer.latest_sync_time_PA)
    deltas = PADelta.objects.all()
    deltas.delete()
    print("PADelta's cleaned up", flush=True)
    return
