import json
from datetime import datetime
from django.db import models
from django.test import TestCase, Client
from django.forms.models import model_to_dict

from .models import PA, AutoStainerStation, PADelta

# Create your tests here.
class PASyncClientSyncTests(TestCase):
    fixtures = ['test_pa.json', 'test_autostainerstation.json', \
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



class PADeltaTests(TestCase):
    fixtures = ['test_autostainerstation.json', 'test_pa.json']

    def test_record_create(self):
        """
        record a create action when a registered autostainer creates PA
        """
        client = Client()
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
        response = client.post('/reagents/api/pa/', json.dumps(test_post), 
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
        client = Client()
        test_post = {
            'alias': 'test_record_create', 
            'incub': 25,
            'ar': 'Low PH',
            'catalog' : 'NAF-0122',
            'autostainer_sn' : 'SN12346'
        }
        
        original = model_to_dict(PA.objects.filter(catalog=test_post['catalog'])[0])
        response = client.put('/reagents/api/pa/NAF-0122/', json.dumps(test_post), \
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
        client = Client()
        test_post = {
            'catalog': ['MAB-0662', 'MAB-0162', 'RAB-0122', 'NAF-0122']
        }

        response = client.delete('/reagents/api/pa/delete/', json.dumps(test_post), \
            content_type='application/json')
        # expect to delete 4 items
        for c in test_post['catalog']:
            obj = PA.objects.filter(catalog=c)
            self.assertEqual(len(obj), 0)
            delta = model_to_dict(PADelta.objects.filter(catalog=c)\
                .filter(operation='DELETE')[0])
            # make sure our entry was actually logged
            self.assertIsNotNone(delta)


class PAViewsTests(TestCase):
    fixtures = ['test_pa.json']
    
    def test_get_all(self):
        """
        test get route works and returns 3 objects from test_pa.json
        """
        client = Client()
        response = client.get('/reagents/api/pa/')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 6)
    
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
            'is_factory': True,
            'date': '2020-08-14T15:09:29-07:00'
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
            'date': '2020-08-14T15:09:29-07:00', 
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
			'date': '2020-08-18T15:09:29-0:700',
			'is_factory': False
		}
        
        catalog = 'MAB-0662'
        response = client.put('/reagents/api/pa/' + catalog + '/', json.dumps(test_post),
            content_type='application/json')
        self.assertEqual(response.status_code, 400)

class ReagentsViewsTests(TestCase):
    fixtures = ['test_autostainerstation.json']

    def test_get_all(self):
        return
        
class AutoStainerStationViewsTests(TestCase):
    fixtures = ['test_autostainerstation.json']
    fields = [field.name for field in AutoStainerStation._meta.fields \
        if not isinstance(field, models.ForeignKey)]

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
            r['latest_sync_time_PA'] = datetime.strptime(r['latest_sync_time_PA'],\
                '%Y-%m-%dT%H:%M:%S%z')
            for f in self.fields:
                self.assertEqual(d[f], r[f])

    def test_get_one_OK(self):
        """
        Test get one works
        """
        client = Client()
        autostainer = AutoStainerStation.objects.get(autostainer_sn='SN12347')
        response = client.get('/reagents/api/autostainer/SN12347/')
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
