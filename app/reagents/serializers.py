# serializers.py
# convert django model data over to JSON or XML format (serialization)
from rest_framework import serializers

from .models import Reagent, AutoStainerStation, PA, PADelta

# information based off of models.py
class ReagentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reagent
        fields = ('autostainer_sn', 'reagent_sn', 'reag_name', 'catalog', 
            'r_type', 'size', 'log', 'vol', 'vol_cur', 'sequence', 'reserved', 
            'mfg_date', 'exp_date', 'edit_date', 'factory')
        
class AutoStainerStationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoStainerStation
        fields = ['autostainer_sn', 'name', 'latest_sync_time_PA']
        extra_kwargs = {'latest_sync_time_PA' : {'required' : False}
        }
        
class PASerializer(serializers.ModelSerializer):
    class Meta:
        model = PA
        fields = ['fullname', 'alias', 'source', 'catalog', 'volume', 'incub', 
            'ar', 'description', 'date', 'is_factory']
        extra_kwargs = {'fullname' : {'required': False},
            'source' : {'required': False},
            'volume' : {'required': False},
            'description': {'required': False},
            'is_factory' : {'required': False}
        }

    

class PADeltaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PADelta
        fields = ['fullname', 'alias', 'source', 'catalog', 'volume', 'incub', 
            'ar', 'description', 'is_factory', 'operation', 'date', 
            'autostainer_sn',]
        extra_kwargs = {'fullname' : {'required': False},
            'alias' : {'required': False},
            'source' : {'required': False},
            'volume' : {'required': False},
            'incub' : {'required': False},
            'ar' : {'required': False},
            'description': {'required': False},
            'is_factory' : {'required': False},
        }

    def __init__(self, *args, **kwargs):
        """Override init for PADeltaSerializer to accept the operation argument
        and generate a timestamp
        """
        operation = kwargs.pop('operation', None)
        if operation:
            kwargs['data']['operation'] = operation
        super(PADeltaSerializer, self).__init__(*args, **kwargs)