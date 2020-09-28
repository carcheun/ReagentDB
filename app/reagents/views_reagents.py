from .models import Reagent, ReagentDelta
from .serializers import ReagentSerializer, ReagentDeltaSerializer
from rest_framework.response import Response
from rest_framework import viewsets, status

# make ya class

    
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
