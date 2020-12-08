from datetime import date
from datetime import datetime
from django.db import models
from django.utils.timezone import now

# Create your models here.

class CommonReagent(models.Model):
    """Reagent Base class
    """
    reag_name = models.TextField(blank=True)
    size = models.TextField(default="S",blank=True)
    log = models.TextField(blank=True)  # Log is actually LOT# .... 
    vol_cur = models.IntegerField(default=3000)
    vol = models.IntegerField(default=3000)
    sequence = models.IntegerField(default=0)
    mfg_date = models.DateField(default=date.today)
    exp_date = models.DateField(default=date.today)
    date = models.DateTimeField(default=now)
    r_type = models.TextField(blank=True)
    factory = models.BooleanField(default=False)
    catalog = models.ForeignKey('PA', on_delete=models.SET_NULL, null=True)
    # which autostainer the reagent is located at
    autostainer_sn = models.ForeignKey('AutoStainerStation', \
        on_delete=models.SET_NULL, blank=True, null=True)


    class Meta:
        abstract = True


# TODO: Add field requirements
# TODO: Add self def for other models
class Reagent(CommonReagent):
    """Reag8 and ReagPA8
    Reagents currently on hand. Reag8 is the inventory of a single
    autostainer, ReagPA8 is the inventory of all autostainers.
    
    Info from ASHome/ReagTbl.h
    """
    # if station is deleted, set to None. If field is none, reagent isnt
    # registered to any autostation machine yet
    # updates the autostainer_sn to indicate which stainer the reagent is
    # stored in
    reagent_sn = models.TextField(primary_key=True)
    in_use = models.BooleanField(default=False)

    class Meta:
        ordering = ('reag_name', 'reagent_sn')

    def is_older(self, date):
        """Returns True if object is older provided given date

        Arguments:
            date: a string representation of datetime
        """
        if self.date < date:
            return True
        return False

    def __str__(self):
        return self.reag_name

    def create_delta(self, operation, autostainer_sn, executor=''):
        """Create a delta entry, given operation and autostainer_sn, entry is
        not yet saved.
        """
        autostainer, created = AutoStainerStation.objects\
            .get_or_create(autostainer_sn=autostainer_sn)
        delta = ReagentDelta(
            reagent_sn = self.reagent_sn,
            reag_name = self.reag_name,
            size = self.size,
            log = self.log,
            vol_cur = self.vol_cur,
            vol = self.vol,
            sequence = self.sequence,
            mfg_date = self.mfg_date,
            exp_date = self.exp_date,
            r_type = self.r_type,
            factory = self.factory,
            catalog = self.catalog,
            autostainer_sn = autostainer,
            operation = operation
        )
        return delta

class ReagentDelta(CommonReagent):
    """Reagent changelog for server
    """
    reagent_sn = models.TextField()
    #CREATE/UPDATE/DELETE
    operation = models.TextField(blank=False)
    #which autostainer performed the action
    executor =  models.ForeignKey('AutoStainerStation', \
        on_delete=models.SET_NULL, blank=True, null=True, \
        related_name='+')

class AutoStainerStation(models.Model):
    """Autostainers identified by S/N, can be given custom name, SN read from 
    INI file on client.
    """
    autostainer_sn = models.TextField(primary_key=True)
    name = models.TextField(null=True, blank=True)
    # Client sends in last sync time registered on their settings.ini, database
    # then determines what needs to to be synced
    # this is for our own records to determine when to tidy up delta database
    latest_sync_time_PA = models.DateTimeField(null=True, blank=True)
    latest_sync_time_Reagent = models.DateTimeField(null=True, blank=True)

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
    catalog = models.TextField(primary_key=True, blank=False)
    
    def is_older(self, date):
        """Returns True if object is older provided given date

        Arguments:
            date: a string representation of datetime
        """
        if self.date < date:
            return True
        return False

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
    # TODO: potential QP 
    #Quick pick, menu selection for PA's
    name = models.TextField()
