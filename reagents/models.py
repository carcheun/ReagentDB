from django.db import models
from django.utils.timezone import now

# Create your models here.

# TODO: Add field requirements
# TODO: Add self def for other models
class Reagent(models.Model):
    """
    Reag8 and ReagPA8
    Reagents currently on hand. Reag8 is the inventory of a single
    autostainer, ReagPA8 is the inventory of all autostainers.
    
    Info from ASHome/ReagTbl.h
    """
    # if station is deleted, set to None. If field is none, reagent isnt
    # registered to any autostation machine yet
    autostainer_sn = models.ForeignKey('AutoStainerStation', on_delete=models.SET_NULL, blank=True, null=True)
    reagent_sn = models.TextField(unique=True)
    reag_name = models.TextField()
    # TODO: potential foreign key right here
    catalog = models.TextField()
    r_type = models.TextField()
    size = models.TextField()
    log = models.TextField()
    vol = models.IntegerField()
    vol_cur = models.IntegerField()
    sequence = models.IntegerField()
    reserved = models.IntegerField()
    mfg_date = models.DateField()
    exp_date = models.DateField()
    edit_date = models.DateTimeField()
    factory = models.BooleanField(default=False)

    def __str__(self):
        return self.reag_name
    
class AutoStainerStation(models.Model):
    """
    Autostainers identified by S/N, can be given custom name
    SN can be the machine name, read from the INI file
    name can be human readable, or just remove it
    """
    autostainer_sn = models.TextField(primary_key=True)
    name = models.TextField()
    # for our own record, so we can delete older change logs
    latest_sync_time_PA = models.DateTimeField()


class CommonInfoPA(models.Model):
    """
    Common values between PA and PADelta
    """
    fullname = models.TextField()
    alias = models.TextField()
    source = models.TextField()
    volume = models.IntegerField(default=0)
    incub = models.IntegerField(default=15)
    ar = models.TextField(default='NO')
    description = models.TextField()
    is_factory = models.BooleanField(default=False)

    class Meta:
        abstract = True

class PA(CommonInfoPA):
    """
    PA_fact8 and PA_user8
    Reagent catalog, not the current reagents on hand
    PA_fact8.d contains reagents sold by factory, PA_user8.d
    are reagents added to catalog by customers
    
    Info from ASHome/PaTbl.h
    """
    # catalog # should be primary key, otherwise PK will be a GUID
    catalog = models.TextField(primary_key=True)
    date = models.DateTimeField(default=now)

    class Meta:
        ordering = ['catalog']

class PADelta(CommonInfoPA):
    """
    A PA change log for the server.
    Changes to the server (from webpage or other clients) are
    listed here and sent to clients when clients request
    updates
    """
    catalog = models.TextField()
    
    # CREATE/UPDATE/DELETE
    operation = models.TextField()
    update_at = models.DateTimeField(default=now)
    # if field is blank, update was provided to the server directly
    autostainer_sn = models.ForeignKey('AutoStainerStation', on_delete=models.SET_NULL, blank=True, null=True)

class QP(models.Model):
    """
    Quick pick, a fine selection of PA's
    """
    name = models.TextField()
