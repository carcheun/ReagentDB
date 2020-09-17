from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.utils.timezone import make_aware
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, action
from .serializers import ReagentSerializer, AutoStainerStationSerializer, PASerializer, PADeltaSerializer
from .models import Reagent, AutoStainerStation, PA, PADelta
from .utils import convert_client_date_format

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
    """ModelViewSet for Reagents, quick easy way to view data
    """
    queryset = Reagent.objects.all()
    serializer_class = ReagentSerializer
    
class AutoStainerStationViewSet(viewsets.ModelViewSet):
    """ModelViewSet for AutoStainerStation
    """
    queryset = AutoStainerStation.objects.all()
    serializer_class = AutoStainerStationSerializer

class PAViewSet(viewsets.ModelViewSet):
    """ModelViewSet for PA

    A timestamped entry is added to PADelta detailing each CUD action, 
    including from whom the entry came from

    TODO: refactor into serialzier?
    TODO: Mostly just refactor
    """
    queryset = PA.objects.all()
    serializer_class = PASerializer

    @action(detail=False, methods=['post'])
    def initial_sync(self, request):
        """Initial sync request. 
        
        Client sends their database to server and server determines if any
        PA's need to be updated or created. PAs are NEVER deleted.

        Args:
            request: empty array, or array containing client database
        
        Returns:
            array containing PA's for client to update or create
        """
        data = JSONParser().parse(request)
        missing = self.queryset.all()
        ret = list()
        for d in data:
            d['date'] = make_aware(convert_client_date_format(d['date']))
            obj, created = self.queryset.get_or_create(
                catalog=d['catalog'],
                defaults={
                    'fullname': d['fullname'], 
                    'alias': d['alias'],
                    'source': d['source'],
                    'volume': d['volume'],
                    'incub': d['incub'], 
                    'ar': d['ar'], 
                    'description': d['description'],
                    'is_factory': d['factory'],
                    'date': d['date']
                }
            )
            if not created:
                # PA already exists, remove from queryset
                missing = missing.exclude(catalog=obj.catalog)
                if obj.is_older(d['date']):
                    # database will update entry if it's older
                    obj.fullname = d['fullname']
                    obj.alias = d['alias']
                    obj.source = d['source']
                    obj.volume = d['volume']
                    obj.incub = d['incub']
                    obj.ar = d['ar']
                    obj.description = d['description']
                    obj.is_factory = d['factory']
                    obj.date = d['date']
                    obj.save()
                else:
                    # database will send the newer entry back to client
                    ret.append(obj)

        ret += list(missing)
        serializer = PASerializer(ret, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def database_to_client_sync(self, request):
        """Client provides sn and last_sync time, returns change log of what 
        the server has done since. Good to call on application startup
        
        Arguments (request):
            autostainer_sn: autostainer serial number provided in settings.ini (?)
            last_sync: timestamp of last time the client sync
        
        Returns:
            PADelta model of all changes greater than last_sync
        """
        data = JSONParser().parse(request)
        last_sync = data.pop('last_sync', None)
        autostainer_sn = data.pop('autostainer_sn', None)

        if not last_sync:
            # we've never sync'd before,
            # TODO: decide what to do if we've never synced before
            return Response(status=status.HTTP_400_BAD_REQUEST)
        dt_last_update = make_aware(convert_client_date_format(last_sync))
        #dt_last_update = make_aware(datetime.strptime(last_sync,\
        #    '%Y-%m-%dT%H:%M:%SZ'))
        missing_changes = PADelta.objects.filter(date__gt=dt_last_update)\
            .exclude(autostainer_sn=autostainer_sn)
        serializer = PADeltaSerializer(missing_changes, many=True)
        print(missing_changes)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def client_to_database_sync(self, request):
        """Client provides the server with a change action. Server determines 
        what changes it requires via latest time stamp

        Arguments (request):
            PA_Delta.db: Except in JSON format
        
        Returns:
            Created or updated entry, or No content if delete
        """
        data = JSONParser().parse(request)
        if data['operation'] == 'CREATE':
            serializer = PASerializer(data=data)
            deltaSerializer = PADeltaSerializer(data=data, operation='CREATE')
            if serializer.is_valid() and deltaSerializer.is_valid():
                serializer.save()
                deltaSerializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif data['operation'] == 'UPDATE':
            # check the timestamp before updating, latest timestamp wins, with server
            # coming as priority
            try:
                pa = PA.objects.get(catalog=data['catalog'])
            except PA.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            dt_updated_at = make_aware(datetime.strptime(data['update_at'],\
                '%Y-%m-%dT%H:%M:%SZ'))
            if pa.date < dt_updated_at:
                deltaSerializer = PADeltaSerializer(data=data, operation='UPDATE')
                serializer = PASerializer(pa, data=data)
                if serializer.is_valid() and deltaSerializer.is_valid():
                    serializer.save()
                    deltaSerializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif data['operation'] == 'DELETE':
            try:
                pa = PA.objects.get(catalog=data['catalog'])
            except PA.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            deltaSerializer = PADeltaSerializer(data=data, operation='DELETE')
            if deltaSerializer.is_valid():
                pa.delete()
                deltaSerializer.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['delete'])
    def delete(self, request):
        # delete multiple PA's, use this method instead
        data = JSONParser().parse(request)
        print(data)
        objects_to_delete = self.queryset.filter(catalog__in=[c for c in data['catalog']])
        objects_to_delete.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, date=None):
        # Override base create method to create PAdelta entry
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
        # Override base create method to create PAdelta entry
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
        # Override base create method to create PAdelta entry
        data = {}
        data['catalog'] = pk
        deltaSerializer = PADeltaSerializer(data=data, operation='DELETE')
        if deltaSerializer.is_valid():
            ret = super().destroy(request, pk)
            if ret.status_code == status.HTTP_204_NO_CONTENT:
                deltaSerializer.save()
            return ret
        else:
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PADeltaViewSet(viewsets.ModelViewSet):
    queryset = PADelta.objects.all()
    serializer_class = PADeltaSerializer