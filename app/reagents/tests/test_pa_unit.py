import json
from datetime import datetime
from django.db import models
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from ..models import PA, AutoStainerStation, PADelta, Reagent, ReagentDelta, User

class PACRUDEndpointTests(APITestCase):
    fixtures = ['test_autostainerstation_set_A.json', 'test_pa_set_A.json', \
        'test_reag_set_A.json']
    username = 'admin'
    password = 'admin'
    
    def setUp(self):
        self.user, created = User.objects.get_or_create(username=self.username)
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
    def test_post_single_PA_OK(self):
        # test single PA POST request and add PA entry
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

        response = self.client.post('/reagents/api/pa/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), test_post)

    def test_post_duplicate_PA_fail(self):
        # test to add duplicate catalog PA
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
        
        response = self.client.post('/reagents/api/pa/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_post_then_put_PA_fail(self):
        # test to try and update PA entry with an already existing catalog
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
        response = self.client.put('/reagents/api/pa/' + catalog + '/', json.dumps(test_post),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_post_then_put_PA_OK(self):
        # test to post and update PA entry
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
        
        response = self.client.post('/reagents/api/pa/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), test_post)
        
        # update a few values
        test_post['fullname'] = 'UPDATED_PA'
        test_post['catalog'] = 'UPD-01235'
        test_post['volume'] = 6000
        
        response = self.client.put('/reagents/api/pa/' + catalog + '/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), test_post)
        
    def test_get_pa_by_alias(self):
        # Get a PA via alias
        alias = 'A0003'
        response = self.client.get('/reagents/api/pa/alias/?alias=' + alias, HTTP_AUTHORIZATION='Token ' + self.token.key)

        r_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_json['fullname'], 'Set_A_0003')
        self.assertEqual(r_json['alias'], 'A0003')
        self.assertEqual(r_json['source'], 'test_pa_set_A.json')
        self.assertEqual(r_json['catalog'], 'CAT0003')
        self.assertEqual(r_json['volume'], 5000)
        self.assertEqual(r_json['incub'], 60)
        self.assertEqual(r_json['ar'], 'High PH')
        self.assertEqual(r_json['description'], 'Dummy Data')
        self.assertEqual(r_json['date'], '2020-08-14T15:09:29-07:00')
        self.assertEqual(r_json['is_factory'], True)

        alias = 'Non_existant'
        response = self.client.get('/reagents/api/pa/alias/?alias=' + alias)
        self.assertEqual(response.status_code, 404)

    def test_initial_sync(self):
        test_post = [{
            # updated
            'fullname': 'Set_A_0003', 
            'alias': 'UPDATE_A0003', 
            'source': 'test_pa_unit.py', 
            'catalog': 'CAT0003', 
            'volume': 5000, 
            'incub': 60, 
            'ar': 'High PH', 
            'description': 'Dummy Data', 
            'date': '2020-08-15T15:09:29', 
            'factory': True
        },
        {
            # failed to update
            'fullname': 'Set_A_0004', 
            'alias': 'A0004_does_not_update', 
            'source': 'test_pa_unit.py', 
            'catalog': 'CAT0004', 
            'volume': 9000, 
            'incub': 15, 
            'ar': 'Low PH', 
            'description': 'Dummy Data', 
            'date': '2020-08-11T15:09:29', 
            'factory': False
        },
        {
            # newly created
            'fullname': 'Newly added PA', 
            'alias': 'new PA', 
            'source': 'test_pa_unit.py', 
            'catalog': 'UPD-01234', 
            'volume': 5000, 
            'incub': 60, 
            'ar': 'High PH', 
            'description': 'Dummy Data', 
            'date': '2020-08-14T15:09:29', 
            'factory': False
        }]
        
        response = self.client.post('/reagents/api/pa/initial_sync/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reagents/api/pa/')
        r_json = response.json()
        self.assertEqual(len(r_json), 6)
        updated_pa = False
        failed_to_update_pa = False
        added_pa = False
        for pa in r_json:
            if pa['catalog'] == 'CAT0003':
                # expect to be updated
                self.assertEqual(pa['alias'], 'UPDATE_A0003')
                self.assertEqual(pa['source'], 'test_pa_unit.py')
                self.assertEqual(pa['volume'], 5000)
                self.assertEqual(pa['incub'], 60)
                self.assertEqual(pa['ar'], 'High PH')
                updated_pa = True
            elif pa['catalog'] == 'CAT0004':
                self.assertEqual(pa['alias'], 'A0004')
                self.assertEqual(pa['source'], 'test_pa_set_A.json')
                self.assertEqual(pa['volume'], 2500)
                self.assertEqual(pa['incub'], 15)
                self.assertEqual(pa['ar'], 'High PH')
                failed_to_update_pa = True
            elif pa['catalog'] == 'UPD-01234':
                self.assertEqual(pa['alias'], 'new PA')
                self.assertEqual(pa['source'], 'test_pa_unit.py')
                self.assertEqual(pa['volume'], 5000)
                self.assertEqual(pa['incub'], 60)
                self.assertEqual(pa['ar'], 'High PH')
                added_pa = True
        self.assertTrue(updated_pa)
        self.assertTrue(failed_to_update_pa)
        self.assertTrue(added_pa)
        
    def test_get_all(self):
        """
        test get route works and returns 3 objects from test_pa.json
        """
        response = self.client.get('/reagents/api/pa/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 5)
    
    def test_get_single_OK(self):
        """
        test get route returns single item
        """
        catalog = 'CAT0002'
        response = self.client.get('/reagents/api/pa/' + catalog + '/')
        
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
        response = self.client.get('/reagents/api/pa/' + catalog + '/')
        
        self.assertEqual(response.status_code, 404)