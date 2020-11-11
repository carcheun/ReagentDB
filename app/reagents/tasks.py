import logging
from celery import shared_task
from .models import Reagent, ReagentDelta, PADelta, AutoStainerStation

logger = logging.getLogger(__name__)

@shared_task
def check_and_remove_PADeltas():
    # remove all deltas older than the earliest Autostainer sycn timestamp
    autostainer = AutoStainerStation.objects.earliest('latest_sync_time_PA')
    deltas = PADelta.objects.filter(date__lte=autostainer.latest_sync_time_PA)
    deltas = PADelta.objects.all()
    deltas.delete()
    return

@shared_task
def check_and_remove_ReagentDeltas():
    # remove all reagent deltas older than the earliest Autostainer sycn timestamp
    autostainer = AutoStainerStation.objects.earliest('latest_sync_time_Reagent')
    deltas = ReagentDelta.objects.filter(date__lte=autostainer.latest_sync_time_Reagent)
    deltas = ReagentDelta.objects.all()
    deltas.delete()
    return

@shared_task
def archive_old_reagents():
    # TODO: either delete or migrate old data to new location
    logger.info("TODO: Archiving finished or expired reagents...")
    return

