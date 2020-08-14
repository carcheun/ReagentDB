from django.contrib import admin

# Register your models here.
from .models import Reagent
from .models import AutoStainerStation
from .models import PA

admin.site.register(Reagent)
admin.site.register(AutoStainerStation)
admin.site.register(PA)