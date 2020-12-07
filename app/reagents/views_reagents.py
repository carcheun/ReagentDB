import logging

from datetime import datetime
from datetime import date
from .models import Reagent, ReagentDelta, PA, AutoStainerStation
from .serializers import ReagentSerializer, ReagentDeltaSerializer
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.utils.timezone import make_aware, now

logger = logging.getLogger(__name__)

class ReagentDeltaViewSet(viewsets.ModelViewSet):
    """ModelViewSet for ReagentsDelta
    """
    queryset = ReagentDelta.objects.all()
    serializer_class = ReagentDeltaSerializer

    
class ReagentViewSet(viewsets.ModelViewSet):
    """ModelViewSet for Reagents
    """
    queryset = Reagent.objects.all()
    serializer_class = ReagentSerializer

    delta_serializer_class = ReagentDeltaSerializer

    @action(detail=False, methods=['post'])
    def lock(self, request):
        """Locked reagents cannot be used in other autostainers. If the reagent
        is being used in one protocol, it will be locked in until the stainig
        is complete

        """
        data = JSONParser().parse(request)

        try:
            reag = Reagent.objects.get(reagent_sn=data['reagent_sn'])
            reag.in_use = data['in_use']
            reag.save()
            serializer = self.serializer_class(reag)
            if data['in_use']:
                logger.info('%s locked', data['reagent_sn'])
            else:
                logger.info('%s unlocked', data['reagent_sn'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Reagent.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'])
    def scan(self, request):
        """During reagent scanning, add the reagent to database if it does not 
        exist. Otherwise return reagent data. The reagent will also be 
        registered to the requesting autostainer client.

        Args:
            JSON containing reagent information

        Returns:
            JSON containing at least cur_vol and log
        """
        data = JSONParser().parse(request)
        # see if reagent exists
        try:
            reag = Reagent.objects.get(reagent_sn=data['reagent_sn'])
            # update the autostainer associated with it
            autostainer, created = AutoStainerStation.objects\
                .get_or_create(autostainer_sn=data['autostainer_sn'])
            reag.autostainer_sn = autostainer
            reag.save()
            serializer = self.serializer_class(reag)
            logger.info("scanned %s", data['reagent_sn'])
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Reagent.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def valid_reagents(self, request):
        """Valid reagents are those whose current volume is greater than or 
        equal to 120

        Returns:
            Valid reagents returned as a list
        """
        query_params = self.request.query_params
        date_filter = self.request.query_params.get('date', None)
        reag = self.queryset.filter(vol_cur__gte=120)
        if date_filter:
            if date_filter[-1] == '/':
                date_filter[:-1]
            try:
                datetime.strptime(date_filter, '%Y-%m-%d')
                reag = reag.filter(date__date=date_filter)
            except ValueError:
                logger.error('Incorrect date format, should be YYYY-MM-DD, not\
                    %s', date_filter)
        serializer = ReagentSerializer(reag, many=True)
        logger.debug(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def database_to_client_sync(self, request):
        """Client provides sn and last_sync_reagent time, and server returns
        change log of what the server has done since. An autostainer entry is 
        created automatically if it does not exist.

        Args:
            autostainer_sn: autostainer serial number provided in settings.ini,
            corresponding to MACHINE parameter
            last_sync_reagent: timestamp of previous client reagent sync 
        
        Returns:
            ReagentDelta model of all changes client is missing
        """
        data = JSONParser().parse(request)
        logger.debug(data)
        last_sync = data.pop('last_sync_reagent', None)
        autostainer_sn = data.pop('autostainer_sn', None)

        autostainer, created = AutoStainerStation.objects\
            .get_or_create(autostainer_sn=autostainer_sn)

        if not last_sync:
            # we've never sync'd before,
            # TODO: decide what to do if we've never synced before
            logger.warning('"last_sync" was None')
            return Response(status=status.HTTP_400_BAD_REQUEST)
        dt_last_update = datetime.strptime(last_sync, '%Y-%m-%dT%H:%M:%S%z')
        missing_changes = ReagentDelta.objects.filter(date__gt=dt_last_update)\
            .exclude(executor=autostainer)
        serializer = ReagentDeltaSerializer(missing_changes, many=True)
        # keep a record of when the last time an autostainer has synced
        autostainer.latest_sync_time_Reagent = now()
        autostainer.save()
        logger.info(serializer.data)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def client_to_database_sync(self, request):
        """Client provides the server with a change action. Server determines 
        what changes it requires via latest time stamp
        
        Arguments (request):
            delta.db: Reagent Table, except in JSON format
                
        Returns:
            http resonse. Details if the request was sucessful or not.
            status codes:
                200/201/204: It is safe for client to delete thier change entry
                400/404: Change did not happen, error sent back to client
        """
        data = JSONParser().parse(request)
        logger.debug(data)

        # sorta validate data, database will generate it's own timestamps for
        # mfg/exp_date if it does not exist
        if data['mfg_date'] == '':
            data.pop('mfg_date')
            logger.warning('"mfg_date" was not provided')
        if data['exp_date'] == '':
            data.pop('exp_date')
            logger.warning('"exp_date" was not provided')

        logger.info("%s %s", data['operation'], data['reagent_sn'])
        deltaSerializer = self.delta_serializer_class(data=data)
        if not deltaSerializer.is_valid():
            logger.error(deltaSerializer.errors)
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        pa, created_pa = PA.objects.get_or_create(catalog=data['catalog'])
        autostainer, created_autostainer = AutoStainerStation.objects\
            .get_or_create(autostainer_sn=data['autostainer_sn'])
            
        if data['operation'] == 'CREATE':
            reagent, created = self.queryset.get_or_create(
                reagent_sn=data['reagent_sn'],
                defaults={
                    'reag_name': data['reag_name'], 
                    'catalog': pa,
                    'size': data['size'],
                    'log': data['log'],
                    'vol': data['vol'], 
                    'vol_cur': data['vol_cur'], 
                    'sequence': data.pop('sequence', 0),
                    'mfg_date': data.pop('mfg_date', date.today()),
                    'exp_date': data.pop('exp_date', date.today()),
                    'factory': data['factory'],
                    'r_type': data['r_type'],
                    'autostainer_sn': autostainer,
                    'date': data['date']
                }
            )
            serializer = self.serializer_class(reagent)
            if created:
                deltaSerializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # TODO: Maybe update instead of create? OR check timestamps and
                # then decide if update or not
                logger.warning('"%s" already exists', data['reagent_sn'])
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif data['operation'] == 'UPDATE':
            # if update... CREATE OR UPDATE!
            try:
                reagent = self.queryset.get(reagent_sn=data['reagent_sn'])
            except Reagent.DoesNotExist:
                logger.warning('"%s" does not exist', data['reagent_sn'])
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = self.serializer_class(reagent, data=data)
            if serializer.is_valid():
                serializer.save()
                deltaSerializer.save()
                return Response(status=status.HTTP_200_OK)
            logger.error(serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif data['operation'] == 'DELETE':
            try:
                reagent = self.queryset.get(reagent_sn=data['reagent_sn'])
                reagent.delete()
            except Reagent.DoesNotExist:
                logger.warning('"%s" does not exist', data['reagent_sn'])
                return Response(status=status.HTTP_404_NOT_FOUND)
            deltaSerializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def sync_batch(self, request):
        ret = list()
        data = JSONParser().parse(request)
        for d in data:
            logger.debug(d)
            pa, created_pa = PA.objects.get_or_create(catalog=d['catalog'])
            # TODO: add PA delta
            if created_pa:
                # TODO: PA probably doesnt come with alias info, so call the alias the
                # catalog?
                logger.warning('%s does not exists, setting PA to None', d['catalog'])
            autostainer, created = AutoStainerStation.objects\
                .get_or_create(autostainer_sn=d['autostainer_sn'])
            d['date'] = datetime.strptime(d['date'], '%Y-%m-%dT%H:%M:%S')
            d['date'] = make_aware(d['date'])
            try:
                obj, created = self.queryset.get_or_create(
                    reagent_sn=d['reagent_sn'],
                    defaults={
                        'reag_name': d['reag_name'], 
                        'catalog': pa,
                        'size': d['size'],
                        'log': d['log'],
                        'vol': d['vol'], 
                        'vol_cur': d['vol_cur'], 
                        'sequence': d.pop('sequence', 0),
                        'mfg_date': d.pop('mfg_date', date.today()),
                        'exp_date': d.pop('exp_date', date.today()),
                        'factory': d['factory'],
                        'r_type': d['r_type'],
                        'autostainer_sn': autostainer,
                        'date': d['date']
                    }
                )
            except Exception as e:
                logger.error(e)
                continue
        serializer = ReagentSerializer(ret, many=True)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def initial_sync(self, request):
        """Initial sync request. 
        
        Client sends their database to server and server determines if any
        reagents's need to be updated or created. Reagents are NEVER deleted.

        Args:
            request: empty array, or array containing client database
        
        Returns:
            array containing reagents's for client to update or create
        """
        data = JSONParser().parse(request)
        missing = self.queryset.all()
        ret = list()
        for d in data:
            logger.debug(d)
            pa, created_pa = PA.objects.get_or_create(catalog=d['catalog'])
            if created_pa:
                logger.warning('%s does not exists, setting PA to None', d['catalog'])
            autostainer, created_autostainer = AutoStainerStation.objects\
                .get_or_create(autostainer_sn=d['autostainer_sn'])
            d['date'] = datetime.strptime(d['date'], '%Y-%m-%dT%H:%M:%S')
            d['date'] = make_aware(d['date'])
            obj, created = self.queryset.get_or_create(
                reagent_sn=d['reagent_sn'],
                defaults={
                    'reag_name': d['reag_name'], 
                    'catalog': pa,
                    'size': d['size'],
                    'log': d['log'],
                    'vol': d['vol'], 
                    'vol_cur': d['vol_cur'], 
                    'sequence': d.pop('sequence', 0),
                    'mfg_date': d.pop('mfg_date', date.today()),
                    'exp_date': d.pop('exp_date', date.today()),
                    'factory': d['factory'],
                    'r_type': d['r_type'],
                    'autostainer_sn': autostainer,
                    'date': d['date']
                }
            )
            if not created:
                # reagent already exists, remove from queryset
                missing = missing.exclude(reagent_sn=obj.reagent_sn)
                if obj.vol_cur < d['vol_cur'] or obj.catalog is None:
                    # database will update entry if it's older
                    obj.reag_name = d['reag_name']
                    obj.catalog = pa
                    obj.size = d['size']
                    obj.log = d['log']
                    obj.vol = d['vol']
                    obj.vol_cur = d['vol_cur']
                    obj.sequence = d.pop('sequence', 0)
                    obj.mfg_date = d.pop('mfg_date', date.today())
                    obj.exp_date = d.pop('exp_date', date.today())
                    obj.factory = d['factory']
                    obj.r_type = d['r_type']
                    obj.autostainer_sn = autostainer
                    obj.date = d['date']
                    obj.save()
                else:
                    # database will send the newer entry back to client
                    ret.append(obj)
        ret += list(missing)
        serializer = ReagentSerializer(ret, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'], url_path='decrease-volume')
    def decrease_volume(self, request, pk=None):
        """Decrease a reagent's volume
        Args:
            request: json with autostainer_sn and dec_vol (int)
        
        Returns:
            Status code 201 if successful
        """
        logger.debug(pk)
        try:
            reagent = Reagent.objects.get(reagent_sn=pk)
        except Reagent.DoesNotExist:
            logger.error('"%s" does not exist', pk)
            return Response(status=status.HTTP_404_NOT_FOUND)
        reagent.vol_cur -= request.data['dec_vol']
        if reagent.vol_cur < 0:
            reagent.vol_cur = 0
        delta = reagent.create_delta(operation='UPDATE',\
            autostainer_sn=request.data['autostainer_sn'],
            executor=request.data['autostainer_sn'])
        delta.save()
        reagent.save()
        serializer = ReagentSerializer(reagent)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create(self, request):
        # override create to method to create reagentdelta entry
        data = request.data.copy()
        data['operation'] = 'CREATE'
        # create the PA if the PA does not exist
        pa, created_pa = PA.objects.get_or_create(catalog=data['catalog'])
        deltaSerializer = self.delta_serializer_class(data=data)

        # if created_pa:
            # TODO: Create PA delta

        if deltaSerializer.is_valid():
            ret = super().create(request)
            if ret.status_code == status.HTTP_201_CREATED:
                deltaSerializer.save()
                logger.info(data)
            return ret
        else:
            logger.error(deltaSerializer.errors) 
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        # override update to method to create reagentdelta entry
        data = request.data.copy()
        data['operation'] = 'UPDATE'
        deltaSerializer = self.delta_serializer_class(data=data)
        if deltaSerializer.is_valid():
            ret = super().update(request, pk)
            if ret.status_code == status.HTTP_200_OK:
                deltaSerializer.save()
                logger.info(data)
            return ret
        else:
            logger.error(deltaSerializer.errors) 
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # override destroy to method to create reagentdelta entry
        data = {}
        data['reagent_sn'] = pk
        data['operation'] = 'DELETE'
        deltaSerializer = self.delta_serializer_class(data=data)
        if deltaSerializer.is_valid():
            ret = super().destroy(request, pk)
            if ret.status_code == status.HTTP_204_NO_CONTENT:
                deltaSerializer.save()
                logger.info(data)
            return ret
        else:
            logger.error(deltaSerializer.errors) 
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)