import json
from datetime import datetime
from django.db import models
from django.test import TestCase, Client
from django.forms.models import model_to_dict

from ..models import PA, AutoStainerStation, PADelta, Reagent, ReagentDelta

class PACRUDEndpointTests(TestCase):
    #fixtures = ['test_autostainerstation_set_A.json', 'test_pa_set_A.json', \
    #    'test_reag_set_A.json']

    fixtures = ['test_autostainerstation_set_A.json', 'test_pa_set_A.json', \
        'test_reag_set_A.json']

    def test_post_single_PA_OK(self):
        # test single PA POST request and add PA entry
        client = Client()
        test_post = {
            'fullname': 'POST_PA', 
            'alias': 'post_PA', 
            'source': 'test_pa_unit.py', 
            'catalog': 'ABC-0123', 
            'volume': 5000, 
            'incub': 60, 
            'ar': 'Low PH', 
            'description': 'Dummy Data', 
            'is_factory': True,
            'date': '2020-08-14T15:09:29-07:00'
        }
        
        response = client.post('/reagents/api/pa/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), test_post)

    def test_post_duplicate_PA_fail(self):
        # test to add duplicate catalog PA
        client = Client()
        test_post = {
            'autostainer': 'SN12346',
            'fullname': 'Set_A_0005', 
            'alias': 'A0005', 
            'source': 'test_pa_set_A.py', 
            'catalog': 'CAT0005', 
            'volume': 5000, 
            'incub': 60, 
            'ar': 'Low PH', 
            'description': 'Dummy Data', 
            'date': '2020-08-14T15:09:29-07:00', 
            'is_factory': False
        }
        
        response = client.post('/reagents/api/pa/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_post_then_put_PA_fail(self):
        # test to try and update PA entry with an already existing catalog
        client = Client()
        test_post = {
            'autostainer': 'SN12346',
			'fullname': 'TSH_update',
			'alias': 'TSH_update',
			'source': 'test_pa_unit.py',
			'catalog': 'MAB-0162',
			'volume': 6000,
			'incub': 20,
			'ar': 'Low PH',
			'description': 'Dummy Data updated',
			'date': '2020-08-18T15:09:29-0:700',
			'is_factory': False
		}
        
        catalog = 'MAB-0662'
        response = client.put('/reagents/api/pa/' + catalog + '/', json.dumps(test_post),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_post_then_put_PA_OK(self):
        # test to post and update PA entry
        client = Client()
        test_post = {
            'fullname': 'UPDATE_PA', 
            'alias': 'update_PA', 
            'source': 'test_pa_unit.py', 
            'catalog': 'UPD-01234', 
            'volume': 5000, 
            'incub': 60, 
            'ar': 'High PH', 
            'description': 'Dummy Data', 
            'date': '2020-08-14T15:09:29-07:00', 
            'is_factory': False
        }
        catalog = test_post['catalog']
        
        response = client.post('/reagents/api/pa/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), test_post)
        
        # update a few values
        test_post['fullname'] = 'UPDATED_PA'
        test_post['catalog'] = 'UPD-01235'
        test_post['volume'] = 6000
        
        response = client.put('/reagents/api/pa/' + catalog + '/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), test_post)
        
    
    def test_get_all(self):
        """
        test get route works and returns 3 objects from test_pa.json
        """
        client = Client()
        response = client.get('/reagents/api/pa/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 5)
    
    def test_get_single_OK(self):
        """
        test get route returns single item
        """
        catalog = 'CAT0002'
        client = Client()
        response =  client.get('/reagents/api/pa/' + catalog + '/')
        
        r_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_json['fullname'], 'Set_A_0002')
        self.assertEqual(r_json['alias'], 'A0002')
        self.assertEqual(r_json['source'], 'test_pa_set_A.json')
        self.assertEqual(r_json['catalog'], 'CAT0002')
        self.assertEqual(r_json['volume'], 5000)
        self.assertEqual(r_json['incub'], 60)
        self.assertEqual(r_json['ar'], 'High PH')
        self.assertEqual(r_json['description'], 'Dummy Data')
        self.assertEqual(r_json['date'], '2020-08-14T15:09:29-07:00')
        self.assertEqual(r_json['is_factory'], True)
        
    def test_get_single_fail(self):
        """
        test get route returns 404 if not available
        """
        catalog = 'MISSING_ITEM'
        client = Client()
        response =  client.get('/reagents/api/pa/' + catalog + '/')
        
        self.assertEqual(response.status_code, 404)