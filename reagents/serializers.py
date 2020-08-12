# serializers.py
# convert django model data over to JSON or XML format (serialization)

from rest_framework import serializers

from .models import Reagent, AutoStainerStation

class ReagentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reagent
        fields = ['reag_name', 'catalog', 'type', 'size', 'sn', 'log', 'vol', 'mfg_date', 'exp_date', 'factory']
        
class AutoStainerStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoStainerStation
        fields = ['sn', 'name']