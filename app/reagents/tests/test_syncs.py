import json
from datetime import datetime
from django.db import models
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase
from django.forms.models import model_to_dict

from ..models import PA, AutoStainerStation, PADelta, User, Reagent, ReagentDelta
class PASyncClientSyncTests(APITestCase):
    fixtures = ['test_pa.json', 'test_autostainerstation_set_A.json', \
        'test_pa_delta.json']
    username = 'admin'
    password = 'admin'
    
    def setUp(self):
        self.user, created = User.objects.get_or_create(username=self.username)
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
    def test_database_to_client_sync(self):
        """
        Send changes that a client is missing, posting to database_to_client_sync
        endpoint
        """
        # autostainer SN12345 requests what happened while it was gone
        test_post = {
            'autostainer_sn': 'SN12345',
            'last_sync': '2020-08-30T11:54:36-0700'
        }
        # should get 2 back
        response = self.client.post('/reagents/api/pa/database_to_client_sync/',\
            json.dumps(test_post), content_type='application/json')

        self.assertEqual(len(response.json()), 2)
        # everything should be after current last sync
        for pa in response.json():
            pa_date = datetime.strptime(pa['date'], '%Y-%m-%dT%H:%M:%S%z')
            autostainer_date = datetime.strptime(test_post['last_sync'], \
                '%Y-%m-%dT%H:%M:%S%z')
            self.assertTrue(pa_date > autostainer_date)


class PASyncTests(APITestCase):
    fixtures = ['test_pa.json', 'test_autostainerstation.json']
    username = 'admin'
    password = 'admin'
    
    def setUp(self):
        self.user, created = User.objects.get_or_create(username=self.username)
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        

    def test_client_to_database_sync(self):
        """
        Send change logs from 2 different autostainers, make sure older changes
        do not happen. Posting to client_to_database_sync endpoint
        """
        SN12345_delta_log = [
            {
                'alias': 'IDH1 R132H', 
                'catalog': 'MAB-0662', 
                'volume': 5000, 
                'incub': 25, # update from 60
                'ar': 'NO', # update from Low PH
                'date': '2020-09-25T14:27:19-07:00', # 9/25 2:27 PM 
                'operation' : 'UPDATE',
                'autostainer_sn' : 'SN12345',
                'is_factory': False
		    },
            {
                'catalog': 'RAB-0122', 
                'date': '2020-09-25T15:58:19-07:00', # 9/25 3:58 PM
                'operation' : 'DELETE',
                'autostainer_sn' : 'SN12345',
		    },
            {
                'alias': 'SYNC Create', 
                'catalog': 'CYN-1234', 
                'volume': 2000, 
                'incub': 60, 
                'ar': 'Low PH', 
                'date': '2020-09-25T16:01:09-07:00', # 9/25 4:91 PM
                'operation' : 'CREATE',
                'autostainer_sn' : 'SN12345',
                'is_factory': False
		    }
        ]
        # will try to edit BEFORE SN12345
        SN12346_delta_log = [
            {
                'alias': 'IDH1 R132H', 
                'catalog': 'MAB-0662', 
                'volume': 500, 
                'incub': 25, # update from 60
                'ar': 'Trypsin', # update from Low PH
                'date': '2020-09-25T14:25:23-07:00', # 9/25 2:25 PM 
                'operation' : 'UPDATE',
                'autostainer_sn' : 'SN12346',
                'is_factory': False
		    },
            {
                'alias': 'IDH1 R132H', 
                'catalog': 'CYN-1234', 
                'volume': 500, 
                'incub': 25, # update from 60
                'ar': 'Trypsin', # update from Low PH
                'date': '2020-09-25T20:25:41-07:00', # 9/25 6:25 PM 
                'operation' : 'UPDATE',
                'autostainer_sn' : 'SN12346',
                'is_factory': False
		    }
        ]

        # send in SN12345 delta first
        #client_to_database_sync
        for entry in SN12345_delta_log:
            response = self.client.post('/reagents/api/pa/client_to_database_sync/',\
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
            response = self.client.post('/reagents/api/pa/client_to_database_sync/',\
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

class ReagentSyncTests(APITestCase):
    fixtures = ['test_autostainerstation_set_A.json', 'test_pa_set_A.json', \
        'test_reag_set_A.json']

    username = 'admin'
    password = 'admin'
            
    def setUp(self):
        self.user, created = User.objects.get_or_create(username=self.username)
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_client_to_database_sync(self):
        SN12346_delta_log = [
            {
                'reagent_sn': 'REAG007', 
                'reag_name': 'New_created_reagent', 
                'size': 'S', 
                'log': 'LOT00003', 
                'catalog': 'CAT0001',
                'vol': 3000, 
                'vol_cur': 2400, 
                'sequence': 0, 
                'mfg_date': '2015-08-14', 
                'exp_date': '2025-08-14', 
                'date': '2020-08-14T15:09:29-07:00', 
                'r_type': '',
                'autostainer_sn': 'SN12346',
                'factory': True,
                'in_use': False,
                'operation' : 'CREATE'
		    },
            {
                'reagent_sn': 'REAG003', 
                'date': '2020-09-25T15:58:19-07:00', # 9/25 3:58 PM
                'operation' : 'DELETE',
                'catalog': 'CAT0002',
                'mfg_date' : '',
                'exp_date' : '',
                'autostainer_sn' : 'SN12346'
		    },
            {
                'reagent_sn': 'REAG002',
                'reag_name': 'UPDATE_TEST_SET_A_1', 
                'size': 'L', 
                'log': 'LOT00003', 
                'catalog': 'CAT0002',
                'vol': 6000, 
                'vol_cur': 3000, 
                'sequence': 0, 
                'mfg_date': '2020-10-25', 
                'exp_date': '2030-12-31', 
                'date': '2020-08-15T15:09:29-07:00', 
                'r_type': '',
                'autostainer_sn': 'SN12346',
                'factory': True,
                'in_use': False,
                'operation': 'UPDATE'
		    }
        ]

        for entry in SN12346_delta_log:
            response = self.client.post('/reagents/api/reagent/client_to_database_sync/',\
                json.dumps(entry), content_type='application/json')

        # expect the changes to have happened
        REAG002 = model_to_dict(Reagent.objects.get(reagent_sn='REAG002'))
        self.assertEqual(REAG002['reag_name'], 'UPDATE_TEST_SET_A_1')
        self.assertEqual(REAG002['vol_cur'], 3000)
        self.assertEqual(REAG002['log'], 'LOT00003')

        REAG007 = Reagent.objects.filter(reagent_sn='REAG007')
        self.assertEqual(len(REAG007), 1)

        REAG003 = Reagent.objects.filter(reagent_sn='REAG003')
        self.assertEqual(len(REAG003), 0)

        # will try to edit BEFORE SN12346
        SN12345_delta_log = [
            {
                'reagent_sn': 'REAG002',
                'reag_name': 'UPDATE_TEST_SET_A_1_LATE', 
                'size': 'L', 
                'log': 'LOT00004', 
                'catalog': 'CAT0002',
                'vol': 6000, 
                'vol_cur': 1200, 
                'sequence': 0, 
                'mfg_date': '2020-10-25', 
                'exp_date': '2030-12-31', 
                'date': '2020-08-15T14:09:29-07:00', # 1 hour before new updates, so they would get overwritten
                'r_type': '',
                'autostainer_sn': 'SN12346',
                'factory': True,
                'in_use': False,
                'operation': 'UPDATE'
		    }
        ]

        for entry in SN12345_delta_log:
            response = self.client.post('/reagents/api/reagent/client_to_database_sync/',\
                json.dumps(entry), content_type='application/json')

        # expect the changes to not happen
        REAG002 = model_to_dict(Reagent.objects.get(reagent_sn='REAG002'))
        self.assertEqual(REAG002['reag_name'], 'UPDATE_TEST_SET_A_1')
        self.assertEqual(REAG002['vol_cur'], 3000)
        self.assertEqual(REAG002['log'], 'LOT00003')