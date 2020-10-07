from datetime import datetime
from .models import Reagent, ReagentDelta, PA, AutoStainerStation
from .serializers import ReagentSerializer, ReagentDeltaSerializer
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, status
from rest_framework.decorators import action

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

    # TODO: endpoint to calculate changes that the client has done offline

    @action(detail=False, methods=['post'])
    def initial_sync(self, request):
        # recieve a list of all reagents that the autostainer has
        # update so that all reagents match incoming data
        data = JSONParser().parse(request)
        missing = self.queryset.all()
        print(data)
        ret = list()
        for d in data:
            # TODO: if autostainer does not exist or PA does not exist, is this
            # the right what to handle?
            try:
                pa = PA.objects.get(catalog=d['catalog'])
            except PA.DoesNotExist:
                pa = None
            autostainer, created = AutoStainerStation.objects\
                .get_or_create(autostainer_sn=d['autostainer_sn'])
            d['date'] = datetime.strptime(d['date'], '%Y-%m-%dT%H:%M:%S.%f%z')
            obj, created = self.queryset.get_or_create(
                reagent_sn=d['reagent_sn'],
                defaults={
                    'reag_name': d['reag_name'], 
                    'catalog': pa,
                    'size': d['size'],
                    'log': d['log'],
                    'vol': d['vol'], 
                    'vol_cur': d['vol_cur'], 
                    'sequence': d['sequence'],
                    'mfg_date': d['mfg_date'],
                    'exp_date': d['exp_date'],
                    'factory': d['factory'],
                    'r_type': d['r_type'],
                    'autostainer_sn': autostainer,
                    'date': d['date']
                }
            )
            if not created:
                # reagent already exists, remove from queryset
                missing = missing.exclude(reagent_sn=obj.reagent_sn)
                if obj.vol_cur < d['vol_cur']:
                    # database will update entry if it's older
                    obj.reag_name = d['reag_name']
                    obj.catalog = pa
                    obj.size = d['size']
                    obj.log = d['log']
                    obj.vol = d['vol']
                    obj.vol_cur = d['vol_cur']
                    obj.sequence = d['sequence']
                    obj.mfg_date = d['mfg_date']
                    obj.exp_date = d['exp_date']
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
        print(data)
        deltaSerializer = self.delta_serializer_class(data=data)
        if deltaSerializer.is_valid():
            ret = super().create(request)
            if ret.status_code == status.HTTP_201_CREATED:
                deltaSerializer.save()
            return ret
        else:
            print(deltaSerializer.errors)
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        # override update to method to create reagentdelta entry
        data = request.data.copy()
        data['operation'] = 'UPDATE'
        print(data)
        deltaSerializer = self.delta_serializer_class(data=data)
        if deltaSerializer.is_valid():
            ret = super().update(request, pk)
            if ret.status_code == status.HTTP_200_OK:
                deltaSerializer.save()
            return ret
        else:
            print(deltaSerializer.errors)
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        # override destroy to method to create reagentdelta entry
        data = {}
        data['reagent_sn'] = pk
        data['operation'] = 'DELETE'
        deltaSerializer = self.delta_serializer_class(data=data)
        print(data)
        if deltaSerializer.is_valid():
            ret = super().destroy(request, pk)
            if ret.status_code == status.HTTP_204_NO_CONTENT:
                deltaSerializer.save()
            return ret
        else:
            print(deltaSerializer.errors)
            return Response(deltaSerializer.errors, status=status.HTTP_400_BAD_REQUEST)