import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
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
def delete_old_reagents():
    # TODO: yearly reagent purge?
    old_reagents = Reagent.objects.filter(vol_cur__lt=120)
    logger.info('Removing empty reagents')
    logger.info(old_reagents)
    old_reagents.delete()
    return

@shared_task
def heartbeat_ping():
    # heart beat ping for clients to know they're still connected to the server
    group_name = 'autostainer_clients'
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_message',
            'message': 'ping'
        }
    )
    return