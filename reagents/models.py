from django.db import models

# Create your models here.

# reagent model
class Reagent(models.Model):
    reag_name = models.TextField()
    catalog = models.TextField()
    type = models.TextField()
    size = models.TextField()
    sn = models.TextField()
    log = models.TextField()
    vol = models.IntegerField()
    mfg_date = models.IntegerField()
    exp_date = models.IntegerField()
    factory = models.IntegerField()
    vol_cur = models.IntegerField()
    sequence = models.IntegerField()
    edit_date = models.IntegerField()
    reserved = models.IntegerField()
    # 2 more edit dates with update DATE and update TIME ??
    # tag who owns the reagent right now, can leave blank
    owned_by = models.ForeignKey("AutoStainerStation", on_delete=models.SET_NULL,  blank=True, null=True)
    
    def __str__(self):
        return self.reag_name
    
# each station should be registered to the database
class AutoStainerStation(models.Model):
    sn = models.TextField()
    name = models.TextField()