from datetime import datetime
from django.db import models
from django.utils.timezone import now
from django.utils.timezone import make_aware

# Create your models here.

# TODO: Add field requirements
# TODO: Add self def for other models
class Reagent(models.Model):
    """Reag8 and ReagPA8
    Reagents currently on hand. Reag8 is the inventory of a single
    autostainer, ReagPA8 is the inventory of all autostainers.
    
    Info from ASHome/ReagTbl.h
    """
    # if station is deleted, set to None. If field is none, reagent isnt
    # registered to any autostation machine yet
    autostainer_sn = models.ForeignKey('AutoStainerStation', \
        on_delete=models.SET_NULL, blank=True, null=True)
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
    """Autostainers identified by S/N, can be given custom name, SN read from 
    INI file on client.
    """
    autostainer_sn = models.TextField(primary_key=True)
    name = models.TextField()
    # Client sends in last sync time registered on their settings.ini, database
    # then determines what needs to to be synced
    # this is for our own records to determine when to tidy up delta database
    latest_sync_time_PA = models.DateTimeField(null=True)


class CommonInfoPA(models.Model):
    """PA base class
    """
    fullname = models.TextField(blank=True)
    alias = models.TextField(blank=True)
    source = models.TextField(blank=True)
    volume = models.IntegerField(default=0)
    incub = models.IntegerField(default=15)
    ar = models.TextField(default='NO')
    description = models.TextField(blank=True)
    is_factory = models.BooleanField(default=False)
    date = models.DateTimeField(default=now)

    class Meta:
        abstract = True

class PA(CommonInfoPA):
    """PA_fact8 and PA_user8
    Reagent catalog, not the current reagents on hand. PA_fact8.d contains 
    reagents sold by factory, PA_user8.d are reagents added to catalog by 
    customers
    
    Info from ASHome/PaTbl.h
    """
    # catalog # should be primary key, otherwise PK will be a GUID
    catalog = models.TextField(primary_key=True)
    
    def is_older(self, date):
        """Returns True if object is older provided given date

        Arguments:
            date: a string representation of datetime
        """
        #if self.date < make_aware(datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')):
        if self.date < date:
            return True
        return False


    #class Meta:
    #    ordering = ['catalog']

class PADelta(CommonInfoPA):
    """A PA change log for the server. Changes to the server (from webpage or 
    other clients) are listed here and sent to clients when clients request
    updates
    """
    catalog = models.TextField()
    
    # CREATE/UPDATE/DELETE
    operation = models.TextField()
    autostainer_sn = models.ForeignKey('AutoStainerStation', \
        on_delete=models.SET_NULL, blank=True, null=True, db_constraint=False)

class QP(models.Model):
    #Quick pick, menu selection for PA's
    name = models.TextField()
