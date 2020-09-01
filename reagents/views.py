from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils.timezone import make_aware
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.decorators import api_view, action
from .serializers import ReagentSerializer, AutoStainerStationSerializer, PASerializer, PADeltaSerializer
from .models import Reagent, AutoStainerStation, PA, PADelta

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
@api_view(['POST', 'GET'])
def pa_recieve_sync(request):
    """
    Client provides the server with a change action
    Server determines what changes it requires via
    latest time stamp
    """
    if request.method == 'POST':
        delta = JSONParser().parse(request)
        # get changes based on catalog, the latest timestamp
        serializer = None
        delta['date'] = delta['updated_at'][:10]
        delta['time'] = delta['updated_at']
        if delta['operation'] == 'CREATE':
            # create an object and save
            serializer = PASerializer(data=delta)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif delta['operation'] == 'UPDATE':
            try:
                pa = PA.objects.get(catalog=delta['catalog'])
            except PA.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            dt_updated_at = make_aware(datetime.strptime(delta['updated_at'], '%Y-%m-%dT%H:%M:%SZ'))
            if pa.time < dt_updated_at:
                serializer = PASerializer(pa, data=delta)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif delta['operation'] == 'DELETE':
            try:
                pa = PA.objects.get(catalog=delta['catalog'])
            except PA.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            pa.delete()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'GET':
        data = JSONParser().parse(request)
        missing_changes = PADelta.objects.filter(update_at__gt=data['last_update'])\
            .exclude(autostainer_sn=data['autostainer_sn'])
        # list of all changes and send it back to the client
        serializer = PADeltaSerializer(missing_changes, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_404_NOT_FOUND)

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
# TODO: maybe add some filters for expired and empty reagents
def reagent_list(request):
    """
    GET all reagents or send POST request to add reagent
    """
    if request.method == 'GET':
        # check if query string exists and then search for
        # all unregistered reagents
        search_unregistered = request.GET.get('registered')
        if search_unregistered and search_unregistered.lower() == 'false':
            reagent = Reagent.objects.filter(autostainer_sn__isnull=True)
        else:
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
def autostainer_get_reagents(request, sn):
    """
    search for reagents currently registered to specified autostainer
    """
    reagents = Reagent.objects.filter(autostainer_sn__exact=sn)
    if reagents is not None:
        serializer = ReagentSerializer(reagents, many=True)
        return Response(serializer.data)
    return Response(status=status.HTTP_404_NOT_FOUND)
    
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
    ModelViewSet for PA, custom create/update/destroy
    in order to log changes into PADelta table
    """
    queryset = PA.objects.all()
    serializer_class = PASerializer

    # custom definitions
    @action(detail=True, methods=['post', 'get'])
    def recieve_sync_request(self, request):
        """
        Client provides the server with a change action
        Server determines what changes it requires via
        latest time stamp
        """
        # giant change lof of things todo
        if request.method == 'POST':
            delta = JSONParser().parse(request)
            # get changes based on catalog, the latest timestamp
            serializer = None
            delta['date'] = delta['updated_at'][:10]
            delta['time'] = delta['updated_at']
            if delta['operation'] == 'CREATE':
                # create an object and save
                return self.create(request)

        return

    def create(self, request):
        data = request.data.copy()
        deltaSerializer = PADeltaSerializer(data=data, operation='CREATE')
        if deltaSerializer.is_valid():
            ret = super().create(request)
            if ret.status_code == status.HTTP_201_CREATED:
                deltaSerializer.save()
            return ret
        else:
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        data = request.data.copy()
        deltaSerializer = PADeltaSerializer(data=data, operation='UPDATE')
        if deltaSerializer.is_valid():
            ret = super().update(request, pk)
            if ret.status_code == status.HTTP_200_OK:
                deltaSerializer.save()
            return ret
        else:
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # find thing, create change log
        data = {}
        data['catalog'] = pk
        deltaSerializer = PADeltaSerializer(data=data, operation='DELETE')
        if deltaSerializer.is_valid():
            ret = super().destroy(request, pk)
            print(ret)
            if ret.status_code == status.HTTP_204_NO_CONTENT:
                print("it is valid!")
                deltaSerializer.save()
            return ret
        else:
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)