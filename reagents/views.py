from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.decorators import api_view
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
@api_view(['GET', 'POST'])
def pa_list(request):
    """
    GET all PA or send POST request to add a new PA
    """
    if request.method == 'GET':
        pa = PA.objects.all()
        serializer = PASerializer(pa, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        # add date and time if letting database handle it
        if 'date' not in data or 'time' not in data:
            time = datetime.now()
            data['date'] = time.strftime('%Y-%m-%d')
            data['time'] = time
        serializer = PASerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def pa_detail(request, catalog):
    """
    Retrieve, update or delete a single PA entry via
    product number
    """
    many_copies = False
    try:
        pa = PA.objects.get(catalog=catalog)
    except PA.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    except PA.MultipleObjectsReturned:
        # multple objects, return just the first one we can find, 
        # but there shouldn't be any duplicate catalog numbers anyway
        pa = PA.objects.filter(catalog=catalog)
        many_copies = True
        
    if request.method == 'GET':
        serializer = PASerializer(pa, many=many_copies)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        # update date and time
        if 'date' not in data or 'time' not in data:
            time = datetime.now()
            data['date'] = time.strftime('%Y-%m-%d')
            data['time'] = time
        serializer = PASerializer(pa, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    elif request.method == 'DELETE':
        pa.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def reagent_detail(request, reagent_sn):
    """
    Retrieve, update or delete a single reagent
    """
    try:
        reagent = Reagent.objects.get(reagent_sn=reagent_sn)
    except Reagent.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ReagentSerializer(reagent)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = ReagentSerializer(reagent, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        reagent.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
        
@csrf_exempt
@api_view(['GET', 'POST'])
def reagent_list(request):
    """
    GET all reagents or send POST request to add reagent
    """
    if request.method == 'GET':
        reagent = Reagent.objects.all()
        serializer = ReagentSerializer(reagent, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ReagentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET', 'POST'])
def autostainerstation_list(request):
    """
    Get a list of the autostation stations currently registered
    """
    if request.method == 'GET':
        autostainer = AutoStainerStation.objects.all()
        serializer = AutoStainerStationSerializer(autostainer, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = AutoStainerStationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def autostainerstation_detail(request, sn):
    """
    Get single autostainerstation or update/delete station details
    """
    many_copies = False
    try:
        autostainer = AutoStainerStation.objects.get(autostainer_sn=sn)
    except AutoStainerStation.DoesNotExist:
        content = {'message' : 'autostainer does not exist'}
        return Response(content, status=status.HTTP_404_NOT_FOUND)
    except AutoStainerStation.MultipleObjectsReturned:
        # handle duplicates, return first one
        autostainer = AutoStainerStation.objects.filter(autostainer_sn=sn)
        many_copies = True
        
    if request.method == 'GET':
        serializer = AutoStainerStationSerializer(autostainer, many=many_copies)
        return Response(serializer.data)
    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = AutoStainerStationSerializer(autostainer, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        autostainer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@csrf_exempt
@api_view(['GET'])
def autostainer_get_current_inventory(request, sn):
    # When I click get inventory, i expect to get
    # whatever I have on hand
    # we are given the auto stainer SN, check reagents database
    # for reagents with auto stainer sn

    # by using django filters __exact we can look for autostainer with sn
    autostainer = AutoStainerStation.objects.filter(autostainer_sn__exact=sn)
    reagents = Reagent.objects.filter()


    return
    
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