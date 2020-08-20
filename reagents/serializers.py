# serializers.py
# convert django model data over to JSON or XML format (serialization)
from rest_framework import serializers

from .models import Reagent, AutoStainerStation, PA

# information based of of models.py
class ReagentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reagent
        fields = ['id', 'reag_name', 'catalog', 'type', 'size', 'sn', 'log', 'vol', 'mfg_date', 
            'exp_date', 'factory', 'vol_cur', 'sequence', 'edit_date', 'reserved', 'owned_by']
        
class AutoStainerStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoStainerStation
        fields = ['id', 'autostainer_sn', 'name']
        
class PASerializer(serializers.ModelSerializer):
    class Meta:
        model = PA
        fields = ('fullname', 'alias', 'source', 'catalog', 'volume', 'incub', 'ar', 'description',
            'factory', 'date', 'time', 'is_factory',)
        extra_kwargs = {'fullname' : {'required': False},
            'source' : {'required': False},
            'volume' : {'required': False},
            'description': {'required': False},
            'factory' : {'required': False},
            'is_factory' : {'required': False}
        }