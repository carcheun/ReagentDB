from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from .serializers import ReagentSerializer, AutoStainerStationSerializer
from .models import Reagent, AutoStainerStation

from django.shortcuts import render

# Create your views here.
def reagents(request, id):
    return HttpResponse("You're looking at reagent %s", id)
    
@csrf_exempt
def reagent_list(request):
    """
    GET all reagents or send POST request to add reagent
    """
    if request.method == 'GET':
        reagent = Reagent.objects.all()
        serializer = ReagentSerializer(reagent, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ReagentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def reagent_detail(request, id):
    """
    Retrieve, update or delete a single reagent
    """
    try:
        reagent = Reagent.objects.get(id=id)
    except reagent.DoesNotExist:
        return HttpResponse(status=404)
        
    if request.method == 'GET':
        serializer = ReagentSerializer(reagent)
        return JsonResponse(serializer.data)
    
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ReagentSerializer(reagent, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JSONResponse(serializer.errors, status=400)
    
    elif request.method == 'DELETE':
        reagent.delete()
        return HttpResponse(status=204)
        
        
# ugly basic render of some data
def index(request):
    all_reagents = Reagent.objects.all()
    context = {
        'all_reagents' : all_reagents,
    }
    
    return render(request, 'reagents/index.html', context)
    
class ReagentViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for Reagents, quick easy way to view data
    """
    # define query
    queryset = Reagent.objects.all()
    # specify serializer to be used
    serializer_class = ReagentSerializer
    
class AutoStainerStation(viewsets.ModelViewSet):
    queryset = AutoStainerStation.objects.all()
    serializer_class = AutoStainerStationSerializer