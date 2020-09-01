# serializers.py
# convert django model data over to JSON or XML format (serialization)
from rest_framework import serializers

from .models import Reagent, AutoStainerStation, PA, PADelta

# information based of of models.py
class ReagentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reagent
        fields = ('autostainer_sn', 'reagent_sn', 'reag_name', 'catalog', 'r_type', 'size', 'log', 'vol', 
            'vol_cur', 'sequence', 'reserved', 'mfg_date', 'exp_date', 'edit_date', 'factory')
        
class AutoStainerStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoStainerStation
        fields = ('autostainer_sn', 'name')
        
class PASerializer(serializers.ModelSerializer):
    class Meta:
        model = PA
        fields = ('fullname', 'alias', 'source', 'catalog', 'volume', 'incub', 'ar', 'description',
            'date', 'time', 'is_factory',)
        extra_kwargs = {'fullname' : {'required': False},
            'source' : {'required': False},
            'volume' : {'required': False},
            'description': {'required': False},
            'is_factory' : {'required': False}
        }

class PADeltaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PADelta
        fields = ('fullname', 'alias', 'source', 'catalog', 'volume', 'incub', 'ar', 'description',
            'is_factory', 'operation', 'update_at', 'autostainer_sn',)
        extra_kwargs = {'fullname' : {'required': False},
            'source' : {'required': False},
            'volume' : {'required': False},
            'description': {'required': False},
            'is_factory' : {'required': False}
        }