from django.contrib import admin

# Register your models here.
from .models import AutoStainerStation
from .models import PA
from .models import PADelta
from .models import Reagent
from .models import ReagentDelta

admin.site.register(AutoStainerStation)
admin.site.register(PA)
admin.site.register(PADelta)
admin.site.register(Reagent)
admin.site.register(ReagentDelta)