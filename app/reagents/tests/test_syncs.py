import json
from datetime import datetime
from django.db import models
from django.test import TestCase, Client
from django.forms.models import model_to_dict

from ..models import PA, AutoStainerStation, PADelta

class PASyncClientSyncTests(TestCase):
    fixtures = ['test_pa.json', 'test_autostainerstation_set_A.json', \
        'test_pa_delta.json']
    
    def test_database_to_client_sync(self):
        """
        Send changes that a client is missing, posting to database_to_client_sync
        endpoint
        """
        client = Client()
        # autostainer SN12345 requests what happened while it was gone
        test_post = {
            'autostainer_sn': 'SN12345',
            'last_sync': '2020-08-30T11:54:36-0700'
        }
        # should get 2 back
        response = client.post('/reagents/api/pa/database_to_client_sync/',\
            json.dumps(test_post), content_type='application/json')
        print(response.json())

class PASyncTests(TestCase):
    fixtures = ['test_pa.json', 'test_autostainerstation.json']

    def test_client_to_database_sync(self):
        """
        Send change logs from 2 different autostainers, make sure older changes
        do not happen. Posting to client_to_database_sync endpoint
        """
        client = Client()
        SN12345_delta_log = [
            {
                "alias": "IDH1 R132H", 
                "catalog": "MAB-0662", 
                "volume": 5000, 
                "incub": 25, # update from 60
                "ar": "NO", # update from Low PH
                "date": "2020-09-25T14:27:19-07:00", # 9/25 2:27 PM 
                "operation" : "UPDATE",
                'autostainer_sn' : 'SN12345',
                "is_factory": False
		    },
            {
                "catalog": "RAB-0122", 
                "date": "2020-09-25T15:58:19-07:00", # 9/25 3:58 PM
                "operation" : "DELETE",
                'autostainer_sn' : 'SN12345',
		    },
            {
                "alias": "SYNC Create", 
                "catalog": "CYN-1234", 
                "volume": 2000, 
                "incub": 60, 
                "ar": "Low PH", 
                "date": "2020-09-25T16:01:09-07:00", # 9/25 4:91 PM
                "operation" : "CREATE",
                'autostainer_sn' : 'SN12345',
                "is_factory": False
		    }
        ]
        # will try to edit BEFORE SN12345
        SN12346_delta_log = [
            {
                "alias": "IDH1 R132H", 
                "catalog": "MAB-0662", 
                "volume": 500, 
                "incub": 25, # update from 60
                "ar": "Trypsin", # update from Low PH
                "date": "2020-09-25T14:25:23-07:00", # 9/25 2:25 PM 
                "operation" : "UPDATE",
                'autostainer_sn' : 'SN12346',
                "is_factory": False
		    },
            {
                "alias": "IDH1 R132H", 
                "catalog": "CYN-1234", 
                "volume": 500, 
                "incub": 25, # update from 60
                "ar": "Trypsin", # update from Low PH
                "date": "2020-09-25T20:25:41-07:00", # 9/25 6:25 PM 
                "operation" : "UPDATE",
                'autostainer_sn' : 'SN12346',
                "is_factory": False
		    }
        ]

        # send in SN12345 delta first
        #client_to_database_sync
        for entry in SN12345_delta_log:
            response = client.post('/reagents/api/pa/client_to_database_sync/',\
                json.dumps(entry), content_type='application/json')
        # expect the changes to have happened
        mab0662 = model_to_dict(PA.objects.get(catalog='MAB-0662'))
        self.assertEqual(mab0662['incub'], 25)
        self.assertEqual(mab0662['ar'], 'NO')
        self.assertEqual(mab0662['incub'], 25)

        rab0122 = PA.objects.filter(catalog='RAB-0122')
        self.assertEqual(len(rab0122), 0)

        cyn1234 = PA.objects.filter(catalog='CYN-1234')
        self.assertEqual(len(cyn1234), 1)

        for entry in SN12346_delta_log:
            response = client.post('/reagents/api/pa/client_to_database_sync/',\
                json.dumps(entry), content_type='application/json')

        # expect first edit did not work
        mab0662 = model_to_dict(PA.objects.get(catalog='MAB-0662'))
        self.assertEqual(mab0662['incub'], 25)
        self.assertEqual(mab0662['ar'], 'NO')
        self.assertEqual(mab0662['incub'], 25)

        cyn1235 = model_to_dict(PA.objects.get(catalog='CYN-1234'))
        self.assertEqual(cyn1235['volume'], 500)
        self.assertEqual(cyn1235['ar'], 'Trypsin')
        self.assertEqual(cyn1235['incub'], 25)


class ReagentSyncTests(TestCase):
    fixtures = ['test_autostainerstation_set_A.json', 'test_pa_set_A.json', \
        'test_reag_set_A.json']

    def test_batch_sync(self):
        print('hi')
        