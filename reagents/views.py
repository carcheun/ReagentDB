from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.parsers import JSONParser, FormParser
from .serializers import ReagentSerializer, AutoStainerStationSerializer, PASerializer
from .models import Reagent, AutoStainerStation, PA

from django.shortcuts import render

# Create your views here.
def hello_world(request):
    return JsonResponse({"HELLO WORLD" : "HI"})
        
# ugly basic render of some data
def index(request):
    all_reagents = Reagent.objects.all()
    context = {
        'all_reagents' : all_reagents,
    }
    
    return render(request, 'reagents/index.html', context)
    
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
def pa_list(request):
    """
    GET all PA or send POST request to add a new PA
    """
    if request.method == 'GET':
        reagent = PA.objects.all()
        serializer = PASerializer(reagent, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = FormParser().parse(request)
        # from here, format date and time to the correct format, if recieved from
        # C++ httplib.h, it will be in x-www-form-urlencoded format
        serializer = PASerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)
        
def pa_detail(request, id):
    """
    Retrieve, update or delete a single PA entry
    """
    try:
        pa = PA.objects.get(id=id)
    except pa.DoesNotExist:
        return HttpResponse(status=404)
    
    if request.method == 'GET':
        serializer = PASerializer(pa)
        return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'PUT':
        print("TODO: PUT DATA")
        return JsonResponse({'status': 'PENDING Function incomplete'})
        
    elif request.method == 'DELETE':
        pa.delete()
        return HttpResponse(status=204)
        

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
    
class ReagentViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for Reagents, quick easy way to view data
    """
    queryset = Reagent.objects.all()
    serializer_class = ReagentSerializer
    
class AutoStainerStationViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for AutoStainerStation, quick easy way to view data
    """
    queryset = AutoStainerStation.objects.all()
    serializer_class = AutoStainerStationSerializer
    
class PAViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for PA, quick easy way to view data
    """
    queryset = PA.objects.all()
    serializer_class = PASerializer