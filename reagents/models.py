from django.db import models

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
    autostainer_sn = models.ForeignKey('AutoStainerStation', on_delete=models.SET_NULL, blank=True, null=True)
    reagent_sn = models.TextField()
    reag_name = models.TextField()
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
    autostainer_sn = models.TextField(unique=True)
    name = models.TextField()

class PA(models.Model):
    """
    PA_fact8 and PA_user8
    Reagent catalog, not the current reagents on hand
    PA_fact8.d contains reagents sold by factory, PA_user8.d
    are reagents added to catalog by customers
    
    Info from ASHome/PaTbl.h
    """
    fullname = models.TextField()
    alias = models.TextField()
    source = models.TextField()
    catalog = models.TextField(unique=True, blank=True)
    volume = models.IntegerField(default=0)
    incub = models.IntegerField()
    ar = models.TextField()
    description = models.TextField()
    factory = models.IntegerField(default=1)
    date = models.DateField()
    time = models.DateTimeField()
    
    # is this reagent from factory or from customer
    # PA_fact8 vs PA_user8
    is_factory = models.BooleanField(default=False)