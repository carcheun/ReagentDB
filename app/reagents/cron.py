from .models import Reagent, ReagentDelta, PADelta, AutoStainerStation

def check_and_remove_PADeltas():
    # remove all deltas older than the earliest Autostainer sycn timestamp
    autostainer = AutoStainerStation.objects.earliest('latest_sync_time_PA')
    deltas = PADelta.objects.filter(date__lte=autostainer.latest_sync_time_PA)
    deltas.delete()
    return