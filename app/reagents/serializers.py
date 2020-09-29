# serializers.py
# convert django model data over to JSON or XML format (serialization)
from rest_framework import serializers

from .models import Reagent, ReagentDelta, AutoStainerStation, PA, PADelta

# information based off of models.py
class ReagentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reagent
        fields = ['autostainer_sn', 'reagent_sn', 'reag_name', 'catalog', 
            'size', 'log', 'vol', 'vol_cur', 'sequence', 'mfg_date', 
            'exp_date', 'date', 'factory', 'r_type']
        extra_kwargs = {'reag_name' : {'required' : False, 'allow_blank': True},
            'size' : {'required' : False},
            'log' : {'required' : False},
            'vol' : {'required' : False},
            'vol_cur' : {'required' : False},
            'sequence' : {'required' : False},
            'mfg_date' : {'required' : False},
            'exp_date' : {'required' : False},
            'date' : {'required' : False},
            'factory' : {'required' : False},
            'r_type' : {'required' : False, 'allow_blank': True},
            'autostainer_sn' : {'required' : False}
        }

class ReagentDeltaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReagentDelta
        fields = ['autostainer_sn', 'reagent_sn', 'reag_name', 'catalog', 
            'size', 'log', 'vol', 'vol_cur', 'sequence', 'mfg_date', 
            'exp_date', 'date', 'factory', 'r_type', 'operation']
        extra_kwargs = {'reag_name' : {'required' : False},
            'size' : {'required' : False},
            'log' : {'required' : False},
            'vol' : {'required' : False},
            'vol_cur' : {'required' : False},
            'sequence' : {'required' : False},
            'mfg_date' : {'required' : False},
            'exp_date' : {'required' : False},
            'date' : {'required' : False},
            'factory' : {'required' : False},
            'r_type' : {'required' : False},
            'autostainer_sn' : {'required' : False}
        }

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
            'alias' : {'required': False, 'allow_blank': True},
            'source' : {'required': False, 'allow_blank': True},
            'volume' : {'required': False},
            'incub' : {'required': False},
            'ar' : {'required': False, 'allow_blank': True},
            'description': {'required': False, 'allow_blank': True},
            'is_factory' : {'required': False},
        }

    def __init__(self, *args, **kwargs):
        """Override init for PADeltaSerializer to accept the operation argument
        and generate a timestamp. Create Autostainer if does not exist
        """
        operation = kwargs.pop('operation', None)
        #autostainer_sn = kwargs['data']['autostainer_sn']
        if operation:
            kwargs['data']['operation'] = operation
        #if autostainer_sn:
        #    AutoStainerStation.objects.get_or_create(autostainer_sn=autostainer_sn)

        super(PADeltaSerializer, self).__init__(*args, **kwargs)