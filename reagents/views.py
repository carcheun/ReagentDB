from django.http import HttpResponse
from django.shortcuts import render
from .models import Reagent, AutoStainerStation

from django.shortcuts import render

# Create your views here.
def reagents(request, id):
    return HttpResponse("You're looking at reagent %s", id)

# ugly basic render of some data
def index(request):
    all_reagents = Reagent.objects.order_by('-reag_name')
    context = {
        'all_reagents' : all_reagents,
    }
    
    return render(request, 'reagents/index.html', context)