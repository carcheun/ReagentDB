import logging

from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import make_aware, now
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, action
from .serializers import AutoStainerStationSerializer, PASerializer, PADeltaSerializer
from .models import Reagent, AutoStainerStation, PA, PADelta
from .utils import convert_client_date_format

logger = logging.getLogger(__name__)

# Create your views here.
def hello_world(request):
    logger.debug("THIS IS A DEBUG!")
    logger.warning("This is a warning!")
    logger.info("This is some info")
    logger.exception("OMG EXCEPTION")
    return JsonResponse({"HELLO WORLD" : "HI"})
        
# ugly basic render of some data
def index(request):
    all_reagents = Reagent.objects.all()
    context = {
        'all_reagents' : all_reagents,
    }
    
    return render(request, 'reagents/index.html', context)

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
    """
    queryset = PA.objects.all()
    serializer_class = PASerializer

    @action(detail=False, methods=['get'])
    def alias(self, request):
        """Get PA by alias

        Request PA by alias via URL request. Works for alias' with forward slash,
        unless it ends in an forward slash

        """
        query_params = self.request.query_params
        alias = query_params.get('alias', None)
        try:
            pa = self.queryset.filter(alias=alias)
        except pa.DoesNotExist:
            logger.error('PA alias "%s" not found!', alias)
            return Response(status=status.HTTP_404_NOT_FOUND)
        # return first PA only
        serializer = PASerializer(pa[0])
        return Response(serializer.data,status=status.HTTP_200_OK)

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
            logger.debug(d)
            d['date'] = datetime.strptime(d['date'], '%Y-%m-%dT%H:%M:%S')
            d['date'] = make_aware(d['date'])
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
        the server has done since. ASHome should call this as as soon as users
        enter the PA dialog. An autostainer entry is created automatically if
        it does not exist.
        
        Arguments (request):
            autostainer_sn: autostainer serial number provided in settings.ini,
            corresponding to MACHINE parameter
            last_sync: timestamp of last time the client sync
        
        Returns:
            PADelta model of all changes greater than last_sync
        """
        data = JSONParser().parse(request)
        logger.debug(data)
        last_sync = data.pop('last_sync', None)
        autostainer_sn = data.pop('autostainer_sn', None)
        
        autostainer, created = AutoStainerStation.objects\
            .get_or_create(autostainer_sn=autostainer_sn)

        if not last_sync:
            # we've never sync'd before,
            # TODO: decide what to do if we've never synced before
            logger.warning('%s "last_sync" was None', autostainer_sn)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        dt_last_update = datetime.strptime(last_sync, '%Y-%m-%dT%H:%M:%S%z')
        missing_changes = PADelta.objects.filter(date__gt=dt_last_update)\
            .exclude(autostainer_sn=autostainer_sn)
        serializer = PADeltaSerializer(missing_changes, many=True)

        # keep a record of when the last time an autostainer has synced
        autostainer.latest_sync_time_PA = now()
        autostainer.save()

        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def client_to_database_sync(self, request):
        """Client provides the server with a change action. Server determines 
        what changes it requires via latest time stamp

        Arguments (request):
            delta.db: PA table, Except in JSON format
        
        Returns:
            http resonse. Details if the request was sucessful or not.
            status codes:
                201/204: It is safe for client to delete thier change entry
                400: Change did not happen, error is sent back to client
                404: Change did not happen, error sent back to client.
                409: Change did not happen, server copy is sent back to client
        """
        data = JSONParser().parse(request)
        logger.debug(data)
        # validate data
        deltaSerializer = PADeltaSerializer(data=data, operation=data['operation'])
        if not deltaSerializer.is_valid():
            logger.error(deltaSerializer.errors)
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        logger.info("%s %s", data['operation'], data['catalog'])
        if data['operation'] == 'CREATE':
            serializer = PASerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                deltaSerializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            # this item already exists, whatever is on the server is the right copy
            if (serializer.errors['catalog'] and data['catalog']):
                pa = PA.objects.get(catalog=data['catalog'])
                return Response(serializer.data, status=status.HTTP_409_CONFLICT)
            logger.error(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif data['operation'] == 'UPDATE':
            # check the timestamp before updating, latest timestamp wins
            try:
                pa = PA.objects.get(catalog=data['catalog'])
            except PA.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            dt_updated_at = datetime.strptime(data['date'],\
                '%Y-%m-%dT%H:%M:%S%z')
            if pa.date < dt_updated_at:
                serializer = PASerializer(pa, data=data)
                if serializer.is_valid():
                    serializer.save()
                    deltaSerializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # return current entry, and 409 to let client know there was a conflict,
                # but that we've returned the 'correct' entry
                serializer = PASerializer(pa)
                return Response(serializer.data, status=status.HTTP_409_CONFLICT)
            return Response(status=status.HTTP_204_NO_CONTENT)
        elif data['operation'] == 'DELETE':
            try:
                pa = PA.objects.get(catalog=data['catalog'])
            except PA.DoesNotExist:
                # if we are deleting we do not care if item exists
                return Response(status=status.HTTP_204_NO_CONTENT)
            pa.delete()
            deltaSerializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'])
    def delete(self, request):
        # delete multiple PA's, use this method instead
        data = JSONParser().parse(request)
        objects_to_delete = self.queryset.filter(catalog__in=[c for c in data['catalog']])
        objects_to_delete.delete()

        for c in data['catalog']:
            logger.info(c)
            cata = {}
            cata['catalog'] = c
            deltaSerializer = PADeltaSerializer(data=cata, operation='DELETE')
            if deltaSerializer.is_valid():
                deltaSerializer.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, date=None):
        # Override base create method to create PAdelta entry
        data = request.data.copy()
        if 'autostainer_sn' in data:
            autostainer, created = AutoStainerStation.objects\
                    .get_or_create(autostainer_sn=data['autostainer_sn'])
        deltaSerializer = PADeltaSerializer(data=data, operation='CREATE')
        if deltaSerializer.is_valid():
            ret = super().create(request)
            if ret.status_code == status.HTTP_201_CREATED:
                deltaSerializer.save()
                logger.info(data)
            return ret
        else:
            logging.error(deltaSerializer.errors)
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def update(self, request, pk=None):
        # Override base create method to create PAdelta entry
        data = request.data.copy()
        if 'autostainer_sn' in data:
            autostainer, created = AutoStainerStation.objects\
                    .get_or_create(autostainer_sn=data['autostainer_sn'])
        deltaSerializer = PADeltaSerializer(data=data, operation='UPDATE')
        if deltaSerializer.is_valid():
            ret = super().update(request, pk)
            if ret.status_code == status.HTTP_200_OK:
                deltaSerializer.save()
                logger.info(data)
            return ret
        else:
            logging.error(deltaSerializer.errors)
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
                logger.info(data)
            return ret
        else:
            logging.error(deltaSerializer.errors)
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PADeltaViewSet(viewsets.ModelViewSet):
    queryset = PADelta.objects.all()
    serializer_class = PADeltaSerializer