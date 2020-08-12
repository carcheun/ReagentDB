from django.contrib import admin

# Register your models here.
from .models import Reagent
from .models import AutoStainerStation

admin.site.register(Reagent)
admin.site.register(AutoStainerStation)