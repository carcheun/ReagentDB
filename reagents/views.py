from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets
from .serializers import ReagentSerializer, AutoStainerStationSerializer
from .models import Reagent, AutoStainerStation

from django.shortcuts import render

# Create your views here.
def reagents(request, id):
    return HttpResponse("You're looking at reagent %s", id)

# ugly basic render of some data
def index(request):
    all_reagents = Reagent.objects.all()
    context = {
        'all_reagents' : all_reagents,
    }
    
    return render(request, 'reagents/index.html', context)
    
class ReagentViewSet(viewsets.ModelViewSet):
    # define query
    queryset = Reagent.objects.all()
    # specify serializer to be used
    serializer_class = ReagentSerializer
    
class AutoStainerStation(viewsets.ModelViewSet):
    queryset = AutoStainerStation.objects.all()
    serializer_class = AutoStainerStationSerializer
    