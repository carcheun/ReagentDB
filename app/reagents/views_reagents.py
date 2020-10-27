from datetime import datetime
from datetime import date
from .models import Reagent, ReagentDelta, PA, AutoStainerStation
from .serializers import ReagentSerializer, ReagentDeltaSerializer
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.utils.timezone import make_aware, now

"""
===============================================
TODO: List cases of how people should use this
1. Open AShome
2. Check if connected to server
3. Sync PA deltas. Do full sync.
4. Sync Reagend deltas. Do full sync.
5. update sync times.
===============================================
"""

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

    @action(detail=False, methods=['get'])
    def valid_reagents(self, request):
        reag = self.queryset.filter(vol_cur__gte=150)
        serializer = ReagentSerializer(reag, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def database_to_client_sync(self, request):
        data = JSONParser().parse(request)
        last_sync = data.pop('last_sync_reagent', None)
        autostainer_sn = data.pop('autostainer_sn', None)

        autostainer, created = AutoStainerStation.objects\
            .get_or_create(autostainer_sn=autostainer_sn)

        if not last_sync:
            # we've never sync'd before,
            # TODO: decide what to do if we've never synced before
            return Response(status=status.HTTP_400_BAD_REQUEST)
        dt_last_update = datetime.strptime(last_sync, '%Y-%m-%dT%H:%M:%S%z')
        missing_changes = ReagentDelta.objects.filter(date__gt=dt_last_update)\
            .exclude(autostainer_sn=autostainer_sn)
        serializer = ReagentDeltaSerializer(missing_changes, many=True)
        # keep a record of when the last time an autostainer has synced
        autostainer.latest_sync_time_Reagent = now()
        autostainer.save()
        return Response(serializer.data,status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def client_to_database_sync(self, request):
        data = JSONParser().parse(request)
        # validate data
        if data['mfg_date'] == '':
            data.pop('mfg_date')
        if data['exp_date'] == '':
            data.pop('exp_date')

        deltaSerializer = self.delta_serializer_class(data=data)
        if not deltaSerializer.is_valid():
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # if CREATE, create if possible
        if data['operation'] == 'CREATE':
            reagent, created = self.queryset.\
                get_or_create(reagent_sn=data['reagent_sn'])
            serializer = self.serializer_class(reagent)
            if created:
                deltaSerializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # TODO: Maybe update instead of create? OR check timestamps and
                # then decide if update or not
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif data['operation'] == 'UPDATE':
            # if update... CREATE OR UPDATE!
            try:
                reagent = self.queryset.get(reagent_sn=data['reagent_sn'])
            except Reagent.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = self.serializer_class(reagent, data=data)
            if serializer.is_valid():
                serializer.save()
                deltaSerializer.save()
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif data['operation'] == 'DELETE':
            try:
                reagent = self.queryset.get(reagent_sn=data['reagent_sn'])
                reagent.delete()
            except Reagent.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            deltaSerializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def initial_sync(self, request):
        # recieve a list of all reagents that the autostainer has
        # update so that all reagents match incoming data
        data = JSONParser().parse(request)
        missing = self.queryset.all()
        ret = list()
        for d in data:
            try:
                pa = PA.objects.get(catalog=d['catalog'])
            except PA.DoesNotExist:
                # TODO: if PA does not exist, should we set as None? Or...?
                pa = None
            autostainer, created = AutoStainerStation.objects\
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
        try:
            reagent = Reagent.objects.get(reagent_sn=pk)
        except Reagent.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        reagent.vol_cur -= request.data['dec_vol']
        if reagent.vol_cur < 0:
            reagent.vol_cur = 0
        delta = reagent.create_delta(operation='UPDATE',\
            autostainer_sn=request.data['autostainer_sn'])

        delta.save()
        reagent.save()
        serializer = ReagentSerializer(reagent)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def create(self, request):
        # override create to method to create reagentdelta entry
        data = request.data.copy()
        data['operation'] = 'CREATE'
        print(data, flush=True)
        deltaSerializer = self.delta_serializer_class(data=data)
        if deltaSerializer.is_valid():
            ret = super().create(request)
            if ret.status_code == status.HTTP_201_CREATED:
                deltaSerializer.save()
            return ret
        else:
            print(deltaSerializer.errors, flush=True)
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
            return ret
        else:
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
            return ret
        else:
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)