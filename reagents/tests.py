import json
from django.test import TestCase, Client

from .models import PA

# Create your tests here.

class PAModelTests(TestCase):
    fixtures = ['test_pa.json']
    
    def test_get_all(self):
        """
        test get route works and returns 3 objects from test_pa.json
        """
        client = Client()
        response = client.get('/reagents/api/pa_list/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
    
    def test_get_single_OK(self):
        """
        test get route returns single item
        """
        catalog = 'MAB-0662'
        client = Client()
        response =  client.get('/reagents/api/pa_list/' + catalog + '/')
        
        r_json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(r_json['fullname'], 'IDH1 R132H')
        self.assertEqual(r_json['alias'], 'IDH1 R132H')
        self.assertEqual(r_json['source'], 'pa_fixture.json')
        self.assertEqual(r_json['catalog'], 'MAB-0662')
        self.assertEqual(r_json['volume'], 5000)
        self.assertEqual(r_json['incub'], 60)
        self.assertEqual(r_json['ar'], 'Low PH')
        self.assertEqual(r_json['description'], 'Dummy Data')
        self.assertEqual(r_json['factory'], 1)
        self.assertEqual(r_json['date'], '2020-08-14')
        self.assertEqual(r_json['time'], '2020-08-14T15:09:29Z')
        self.assertEqual(r_json['is_factory'], True)
        
    def test_get_single_fail(self):
        """
        test get route returns 404 if not available
        """
        catalog = 'MISSING_ITEM'
        client = Client()
        response =  client.get('/reagents/api/pa_list/' + catalog + '/')
        
        self.assertEqual(response.status_code, 404)
        
    def test_post_single_PA_OK(self):
        """
        test single PA POST request and add PA entry
        """
        client = Client()
        test_post = {
            'fullname': 'POST_PA', 
            'alias': 'post_PA', 
            'source': 'tests.py', 
            'catalog': 'ABC-0123', 
            'volume': 5000, 
            'incub': 60, 
            'ar': 'Low PH', 
            'description': 'Dummy Data', 
            'factory': 1, 
            'date': '2020-08-14', 
            'time': '2020-08-14T15:09:29Z', 
            'is_factory': False
        }
        
        response = client.post('/reagents/api/pa_list/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), test_post)
        
    def test_post_duplicate_PA_fail(self):
        """
        test to add duplicate catalog PA
        """
        client = Client()
        test_post = {
            'fullname': 'DUPLICATE_POST_PA', 
            'alias': 'duplicate_post_pa', 
            'source': 'tests.py', 
            'catalog': 'RAB-0122', 
            'volume': 5000, 
            'incub': 60, 
            'ar': 'Low PH', 
            'description': 'Dummy Data', 
            'factory': 1, 
            'date': '2020-08-14', 
            'time': '2020-08-14T15:09:29Z', 
            'is_factory': False
        }
        
        response = client.post('/reagents/api/pa_list/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
    def test_post_then_put_PA_OK(self):
        """
        test to update PA entry
        """
        client = Client()
        test_post = {
            'fullname': 'UPDATE_PA', 
            'alias': 'update_PA', 
            'source': 'tests.py', 
            'catalog': 'UPD-01234', 
            'volume': 5000, 
            'incub': 60, 
            'ar': 'High PH', 
            'description': 'Dummy Data', 
            'factory': 1, 
            'date': '2020-08-14', 
            'time': '2020-08-14T15:09:29Z', 
            'is_factory': False
        }
        catalog = test_post['catalog']
        
        response = client.post('/reagents/api/pa_list/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), test_post)
        
        # update a few values
        test_post['fullname'] = 'UPDATED_PA'
        test_post['catalog'] = 'UPD-01235'
        test_post['volume'] = 6000
        
        response = client.put('/reagents/api/pa_list/' + catalog + '/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), test_post)
        
    def test_post_then_put_PA_fail(self):
        """
        test to try and update PA entry with an already existing catalog
        """
        client = Client()
        test_post = {
			'fullname': 'TSH_update',
			'alias': 'TSH_update',
			'source': 'tests.py',
			'catalog': 'MAB-0162',
			'volume': 6000,
			'incub': 20,
			'ar': 'Low PH',
			'description': 'Dummy Data updated',
			'factory': 1,
			'date': '2020-08-18',
			'time': '2020-08-18T15:09:29Z',
			'is_factory': False
		}
        
        catalog = 'MAB-0662'
        response = client.put('/reagents/api/pa_list/' + catalog + '/', json.dumps(test_post),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        