from datetime import datetime
from .models import Reagent, ReagentDelta
from .serializers import ReagentSerializer, ReagentDeltaSerializer
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, status
from rest_framework.decorators import action

class ReagentDeltaViewSet(viewsets.ModelViewSet):
    """ModelViewSet for Reagents
    """
    queryset = ReagentDelta.objects.all()
    serializer_class = ReagentDeltaSerializer

    
class ReagentViewSet(viewsets.ModelViewSet):
    """ModelViewSet for Reagents
    """
    queryset = Reagent.objects.all()
    serializer_class = ReagentSerializer

    delta_serializer_class = ReagentDeltaSerializer

    # action to synchronize reagents

    @action(detail=False, methods=['post'])
    def initial_sync(self, request):
        # recieve a list of all reagents that the autostainer has
        # update so that all reagents match incoming data
        data = JSONParser().parse(request)
        missing = self.queryset.all()
        ret = list()
        for d in data:
            d['date'] = datetime.strptime(d['date'], '%Y-%m-%dT%H:%M:%S.%f%z')
            obj, created = self.queryset.get_or_create(
                reagent_sn=d['reagent_sn'],
                defaults={
                    'reag_name': d['reag_name'], 
                    'catalog': d['catalog'],
                    'size': d['size'],
                    'log': d['log'],
                    'vol': d['vol'], 
                    'vol_cur': d['vol_cur'], 
                    'sequence': d['sequence'],
                    'mfg_date': d['mfg_date'],
                    'exp_date': d['exp_date'],
                    'factory': d['factory'],
                    'r_type': d['r_type'],
                    'autostainer_sn': d['autostainer_sn'],
                    'date': d['date']
                }
            )
            if not created:
                # reagent already exists, remove from queryset
                missing = missing.exclude(reagent_sn=obj.reagent_sn)
                if obj.is_older(d['date']):
                    # database will update entry if it's older
                    obj.reag_name = d['reag_name']
                    obj.catalog = d['catalog']
                    obj.size = d['size']
                    obj.log = d['log']
                    obj.vol = d['vol']
                    obj.vol_cur = d['vol_cur']
                    obj.sequence = d['sequence']
                    obj.mfg_date = d['mfg_date']
                    obj.exp_date = d['exp_date']
                    obj.factory = d['factory']
                    obj.r_type = d['r_type']
                    obj.autostainer_sn = d['autostainer_sn']
                    obj.date = d['date']
                    obj.save()
                else:
                    # database will send the newer entry back to client
                    ret.append(obj)

        ret += list(missing)
        serializer = ReagentSerializer(ret, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


    def create(self, request, date=None):
        # override create to method to create reagentdelta entry
        data = request.data.copy()
        data['operation'] = 'CREATE'
        deltaSerializer = self.delta_serializer_class(data=data)
        if deltaSerializer.is_valid():
            ret = super().create(request)
            if ret.status_code == status.HTTP_201_CREATED:
                deltaSerializer.save()
            return ret
        else:
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
