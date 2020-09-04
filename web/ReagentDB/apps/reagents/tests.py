import json
from django.test import TestCase, Client
from django.forms.models import model_to_dict

from .models import PA, AutoStainerStation

# Create your tests here.

class PAViewsTests(TestCase):
    fixtures = ['test_pa.json']
    
    def test_get_all(self):
        """
        test get route works and returns 3 objects from test_pa.json
        """
        client = Client()
        response = client.get('/reagents/api/pa/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
    
    def test_get_single_OK(self):
        """
        test get route returns single item
        """
        catalog = 'MAB-0662'
        client = Client()
        response =  client.get('/reagents/api/pa/' + catalog + '/')
        
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
        response =  client.get('/reagents/api/pa/' + catalog + '/')
        
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
        
        response = client.post('/reagents/api/pa/', json.dumps(test_post), 
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
        
        response = client.post('/reagents/api/pa/', json.dumps(test_post), 
            content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
    def test_post_then_put_PA_OK(self):
        """
        test to post and update PA entry
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
        response = client.put('/reagents/api/pa/' + catalog + '/', json.dumps(test_post),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)

class ReagentsViewsTests(TestCase):
    fixtures = ['test_autostainerstation.json']

    def test_get_all(self):
        print('OK')
        
class AutoStainerStationViewsTests(TestCase):
    fixtures = ['test_autostainerstation.json']
    fields = [field.name for field in AutoStainerStation._meta.get_fields()]
    fields.pop(0)

    def test_get_all(self):
        """
        Test get route works and returns all stainers
        """
        client = Client()
        response = client.get('/reagents/api/autostainer/')
        autostainer = AutoStainerStation.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), autostainer.count())

        for a_fixture, r in zip(autostainer, response.json()):
            d = model_to_dict(a_fixture)
            for f in self.fields:
                self.assertEqual(d[f], r[f])

    def test_get_one_OK(self):
        """
        Test get one works
        """
        client = Client()
        response = client.get('/reagents/api/autostainer/SN12347/')
        autostainer = AutoStainerStation.objects.get(autostainer_sn='SN12347')

        d = model_to_dict(autostainer)
        for f in self.fields:
            self.assertEqual(d[f], response.json()[f])

    def test_get_one_fail(self):
        """
        Return a 404 error when stainer isnt in database
        """
        client = Client()
        response = client.get('/reagents/api/autostainer/DUMMYSN/')
        autostainer = AutoStainerStation.objects.filter(autostainer_sn='DUMMYSN').first()

        self.assertEqual(response.status_code, 404)
        self.assertIsNone(autostainer)

    def test_post_single_autostainer(self):
        """
        Post request add an autostainer
        """
        client = Client()
        test_post = {
			'autostainer_sn': 'CYN1014',
			'name': 'Carolyns Autostainer'
		}
        
        response = client.post('/reagents/api/autostainer/', json.dumps(test_post),
            content_type='application/json')
        autostainer = AutoStainerStation.objects.filter(autostainer_sn='CYN1014').first()
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(autostainer)

    def test_delete_single_autostainer(self):
        """
        Delete an autostainer
        """
        autostainer = AutoStainerStation.objects.all()
        d = model_to_dict(autostainer[0])
        sn = d['autostainer_sn']

        client = Client()
        response = client.delete('/reagents/api/autostainer/' + sn + '/')
        deleted_autostainer = AutoStainerStation.objects.filter(autostainer_sn=sn).first()
        self.assertIsNone(deleted_autostainer)
