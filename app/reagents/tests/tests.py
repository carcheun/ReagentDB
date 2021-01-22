import json
from datetime import datetime
from django.db import models
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token
from django.forms.models import model_to_dict

from ..models import PA, AutoStainerStation, PADelta, User

# Create your tests here.
class PADeltaTests(APITestCase):
    fixtures = ['test_autostainerstation.json', 'test_pa.json']
    username = 'admin'
    password = 'admin'
    
    def setUp(self):
        self.user, created = User.objects.get_or_create(username=self.username)
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_record_create(self):
        """
        record a create action when a registered autostainer creates PA
        """
        test_post = {
            'fullname': 'PADeltaTests test_record_create', 
            'alias': 'test_record_create', 
            'source': 'tests.py', 
            'catalog': 'CREATE0001', 
            'volume': 5000, 
            'incub': 60, 
            'ar': 'High PH', 
            'description': 'Dummy Data', 
            'autostainer_sn' : 'SN12345',
            'is_factory': False
        }
        
        # send the request
        response = self.client.post('/reagents/api/pa/', json.dumps(test_post), 
            content_type='application/json')
        delta = model_to_dict(PADelta.objects.latest('date'))
        self.assertEqual(test_post['fullname'], delta['fullname'])
        self.assertEqual(test_post['alias'], delta['alias'])
        self.assertEqual(test_post['source'], delta['source'])
        self.assertEqual(test_post['catalog'], delta['catalog'])
        self.assertEqual(test_post['volume'], delta['volume'])
        self.assertEqual(test_post['incub'], delta['incub'])
        self.assertEqual(test_post['ar'], delta['ar'])
        self.assertEqual(test_post['description'], delta['description'])
        self.assertEqual(test_post['autostainer_sn'], delta['autostainer_sn'])
        self.assertEqual(test_post['is_factory'], delta['is_factory'])
        self.assertEqual(delta['operation'], 'CREATE')
        self.assertEqual(response.status_code, 201)

    def test_record_update(self):
        """
        record an update action when registered autostainer edits PA
        """
        test_post = {
            'alias': 'test_record_create', 
            'incub': 25,
            'ar': 'Low PH',
            'catalog' : 'NAF-0122',
            'autostainer_sn' : 'SN12346'
        }
        
        original = model_to_dict(PA.objects.filter(catalog=test_post['catalog'])[0])
        response = self.client.put('/reagents/api/pa/NAF-0122/', json.dumps(test_post), \
            content_type='application/json')
        delta = model_to_dict(PADelta.objects.latest('date'))
        updated = model_to_dict(PA.objects.filter(catalog=test_post['catalog'])[0])

        self.assertEqual(original['fullname'], updated['fullname'])
        self.assertNotEqual(original['alias'], updated['alias'])
        self.assertEqual(original['source'], updated['source'])
        self.assertEqual(test_post['catalog'], delta['catalog'])
        self.assertEqual(original['volume'], updated['volume'])
        self.assertNotEqual(original['incub'], updated['incub'])
        self.assertNotEqual(original['ar'], updated['ar'])
        self.assertEqual(original['description'], updated['description'])
        self.assertEqual(test_post['autostainer_sn'], delta['autostainer_sn'])
        self.assertEqual(original['is_factory'], updated['is_factory'])
        self.assertEqual(delta['operation'], 'UPDATE')
        self.assertEqual(delta['incub'], test_post['incub'])
        self.assertEqual(delta['ar'], test_post['ar'])
        self.assertEqual(response.status_code, 200)

    def test_record_delete(self):
        """
        test delete entry gets recorded
        """
        test_post = {
            'catalog': ['MAB-0662', 'MAB-0162', 'RAB-0122', 'NAF-0122']
        }

        response = self.client.delete('/reagents/api/pa/delete/', json.dumps(test_post), \
            content_type='application/json')
        # expect to delete 4 items
        for c in test_post['catalog']:
            obj = PA.objects.filter(catalog=c)
            self.assertEqual(len(obj), 0)
            delta = model_to_dict(PADelta.objects.filter(catalog=c)\
                .filter(operation='DELETE')[0])
            # make sure our entry was actually logged
            self.assertIsNotNone(delta)

class ReagentsViewsTests(APITestCase):
    fixtures = ['test_autostainerstation.json']

    def test_get_all(self):
        return
        
class AutoStainerStationViewsTests(APITestCase):
    password = 'admin'
    username = 'admin'
    fixtures = ['test_autostainerstation.json']
    fields = [field.name for field in AutoStainerStation._meta.fields \
        if not isinstance(field, models.ForeignKey)]
    
    def setUp(self):
        self.user, created = User.objects.get_or_create(username=self.username)
        self.token, created = Token.objects.get_or_create(user=self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

    def test_get_all(self):
        """
        Test get route works and returns all stainers
        """
        response = self.client.get('/reagents/api/autostainer/')
        autostainer = AutoStainerStation.objects.all()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), autostainer.count())

        for a_fixture, r in zip(autostainer, response.json()):
            d = model_to_dict(a_fixture)
            r['latest_sync_time_PA'] = datetime.strptime(r['latest_sync_time_PA'],\
                '%Y-%m-%dT%H:%M:%S%z')
            for f in self.fields:
                self.assertEqual(d[f], r[f])

    def test_get_one_OK(self):
        """
        Test get one works
        """
        autostainer = AutoStainerStation.objects.get(autostainer_sn='SN12347')
        response = self.client.get('/reagents/api/autostainer/SN12347/')
        d = model_to_dict(autostainer)
        r = response.json()
        r['latest_sync_time_PA'] = datetime.strptime(r['latest_sync_time_PA'],\
            '%Y-%m-%dT%H:%M:%S%z')
        for f in self.fields:
            self.assertEqual(d[f], response.json()[f])

    def test_get_one_fail(self):
        """
        Return a 404 error when stainer isnt in database
        """
        response = self.client.get('/reagents/api/autostainer/DUMMYSN/')
        autostainer = AutoStainerStation.objects.filter(autostainer_sn='DUMMYSN').first()

        self.assertEqual(response.status_code, 404)
        self.assertIsNone(autostainer)

    def test_post_single_autostainer(self):
        """
        Post request add an autostainer
        """
        test_post = {
			'autostainer_sn': 'CYN1014',
			'name': 'Carolyns Autostainer'
		}
        
        response = self.client.post('/reagents/api/autostainer/', json.dumps(test_post),
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

        response = self.client.delete('/reagents/api/autostainer/' + sn + '/')
        deleted_autostainer = AutoStainerStation.objects.filter(autostainer_sn=sn).first()
        self.assertIsNone(deleted_autostainer)
