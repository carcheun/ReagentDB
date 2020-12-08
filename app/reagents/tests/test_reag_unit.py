import json
from datetime import datetime
from django.db import models
from django.test import TestCase, Client
from django.forms.models import model_to_dict

from ..models import PA, AutoStainerStation, PADelta, Reagent, ReagentDelta

# Create your tests here.
class ReagentEndpointTests(TestCase):
    fixtures = ['test_autostainerstation_set_A.json', 'test_pa_set_A.json', \
        'test_reag_set_A.json']
    
    def test_lock_reagent(self):
        #Send command to lock reagent
        reag = Reagent.objects.get(reagent_sn='REAG001')
        reag.in_use = False
        reag.save()
        self.assertFalse(reag.in_use)

        client = Client()
        test_post = {
            'reagent_sn': 'REAG001',
            'in_use': True
        }
        # check that reagent is now locked
        response = client.post('/reagents/api/reagent/lock/',\
            json.dumps(test_post), content_type='application/json')
        
        reag = Reagent.objects.get(reagent_sn='REAG001')
        self.assertTrue(reag.in_use)

    def test_unlock_reagent(self):
        #Send command to unlock reagent
        reag = Reagent.objects.get(reagent_sn='REAG001')
        reag.in_use = True
        reag.save()

        client = Client()
        test_post = {
            'reagent_sn': 'REAG001',
            'in_use': False
        }
        # check that reagent is now locked
        response = client.post('/reagents/api/reagent/lock/',\
            json.dumps(test_post), content_type='application/json')
        
        reag = Reagent.objects.get(reagent_sn=test_post['reagent_sn'])
        self.assertFalse(reag.in_use)

    def test_scan_reagent(self):
        test_post = {
            'reagent_sn': 'REAG001',
            'autostainer_sn': 'SN12345'
        }
        client = Client()
        response = client.post('/reagents/api/reagent/scan/',\
            json.dumps(test_post), content_type='application/json')
        
        # scanned data should return
        reag = Reagent.objects.get(reagent_sn=test_post['reagent_sn'])
        self.assertEqual(reag.vol_cur, response.json()['vol_cur'])
        self.assertEqual(reag.vol, response.json()['vol'])
        self.assertEqual(reag.reag_name, response.json()['reag_name'])
        exp_date_str = reag.exp_date.strftime('%Y-%m-%d')
        self.assertEqual(exp_date_str, response.json()['exp_date'])
        self.assertEqual(reag.log, response.json()['log'])
        self.assertEqual(reag.autostainer_sn.autostainer_sn, response.json()['autostainer_sn'])

    def test_scan_reagent_missing_autostainer(self):
        test_post = {
            'reagent_sn': 'REAG001',
            'autostainer_sn': 'SN_NON_EXISTANT'
        }
        client = Client()
        response = client.post('/reagents/api/reagent/scan/',\
            json.dumps(test_post), content_type='application/json')
        # scanned data should return, but a new autostainer should
        # also be made
        reag = Reagent.objects.get(reagent_sn=test_post['reagent_sn'])
        self.assertEqual(reag.vol_cur, response.json()['vol_cur'])
        self.assertEqual(reag.vol, response.json()['vol'])
        self.assertEqual(reag.reag_name, response.json()['reag_name'])
        exp_date_str = reag.exp_date.strftime('%Y-%m-%d')
        self.assertEqual(exp_date_str, response.json()['exp_date'])
        self.assertEqual(reag.log, response.json()['log'])
        self.assertEqual(reag.autostainer_sn.autostainer_sn, response.json()['autostainer_sn'])

    def test_scan_missing_reagent(self):
        test_post = {
            'reagent_sn': 'MISSING_REAGENT',
            'autostainer_sn': 'SN_NON_EXISTANT'
        }
        client = Client()
        response = client.post('/reagents/api/reagent/scan/',\
            json.dumps(test_post), content_type='application/json')
        self.assertEqual(404, response.status_code)

    def test_valid_reagents(self):
        #Returned reagents are all above 150ul and not expired
        client = Client()
        ret = client.get('/reagents/api/reagent/valid_reagents/')
        reags = Reagent.objects.filter(vol_cur__gte=150)
        self.assertEqual(len(ret.json()), reags.count())
        
    def test_valid_reagents_date_filter(self):
        # Returned reagents are all above 150ul and not expired
        # along with a date filter
        client = Client()
        ret = client.get('/reagents/api/reagent/valid_reagents/?date=2020-08-14/')
        date_filter = '2020-08-14'
        datetime.strptime(date_filter, '%Y-%m-%d')
        reags = Reagent.objects.filter(vol_cur__gte=150, date__date=date_filter)
        self.assertEqual(len(ret.json()), reags.count())

    def test_decrease_volume(self):
        # decrease volume and check
        reagent_sn = 'REAG002'
        dec_vol = 250

        client = Client()
        reag = Reagent.objects.get(reagent_sn=reagent_sn)
        vol_cur = reag.vol_cur

        test_post = {
            'dec_vol': dec_vol,
            'autostainer_sn': 'STAINER0001'
        }

        response = client.put('/reagents/api/reagent/' + reagent_sn + '/decrease-volume/',\
            json.dumps(test_post), content_type='application/json')
        reag = Reagent.objects.get(reagent_sn=reagent_sn)
        delta = ReagentDelta.objects.latest('date')
        self.assertEqual(vol_cur - dec_vol, delta.vol_cur)
        self.assertEqual("UPDATE", delta.operation)
        self.assertEqual(vol_cur - dec_vol, reag.vol_cur)

    def test_decrease_volume_past_zero(self):
        # decrease past 0 and it will be 0
        reagent_sn = 'REAG006'
        dec_vol = 100

        client = Client()
        reag = Reagent.objects.get(reagent_sn=reagent_sn)
        
        test_post = {
            'dec_vol': dec_vol,
            'autostainer_sn': 'STAINER0001'
        }

        response = client.put('/reagents/api/reagent/' + reagent_sn + '/decrease-volume/',\
            json.dumps(test_post), content_type='application/json')
        reag = Reagent.objects.get(reagent_sn=reagent_sn)
        self.assertEqual(0, reag.vol_cur)


class ReagentCRUDEndpointTests(TestCase):
    fixtures = ['test_autostainerstation_set_A.json', 'test_pa_set_A.json', \
        'test_reag_set_A.json']
    
    def test_create_reagent(self):
        # check that a delta is created as well
        test_post = {
            'reagent_sn': 'REAG007',
            'reag_name': 'New Reagent',
            'size': 'M',
            'catalog': 'CAT0005',
            'vol': 6500,
            'vol_cur': 6500,
            'mfg_date': '2020-12-07',
            'exp_date': '2030-12-07',
            'r_type': 'ar',
            'factory': True,
            'autostainer_sn': 'STAINER0001'
        }
        
        client = Client()
        ret = client.post('/reagents/api/reagent/',\
            json.dumps(test_post), content_type='application/json')
        self.assertEqual(201, ret.status_code)
        
        reag = Reagent.objects.get(reagent_sn=test_post['reagent_sn'])
        self.assertFalse(reag.in_use)
        self.assertEqual(reag.size, test_post['size'])
        self.assertEqual(reag.log, test_post['log'])
        self.assertEqual(reag.vol_cur, test_post['vol_cur'])
        self.assertEqual(reag.vol, test_post['vol'])
        self.assertEqual(reag.sequence, test_post['sequence'])
        self.assertEqual(reag.mfg_date, test_post['mfg_date'])
        self.assertEqual(reag.exp_date, test_post['exp_date'])
        self.assertEqual(reag.r_type, test_post['r_type'])
        self.assertEqual(reag.factory, test_post['factory'])
        self.assertEqual(reag.catalog, test_post['catalog'])

        delta = model_to_dict(ReagentDelta.objects.latest('date'))
        self.assertFalse(reag.in_use)
        self.assertEqual(reag.size, delta.size)
        self.assertEqual(reag.autostainer_sn, delta.autostainer_sn)
        self.assertEqual(reag.reagent_sn, delta.reagent_sn)
        self.assertEqual(reag.log, delta.log)
        self.assertEqual(reag.vol_cur, delta.vol_cur)
        self.assertEqual(reag.vol, delta.vol)
        self.assertEqual(reag.sequence, delta.sequence)
        self.assertEqual(reag.mfg_date, delta.mfg_date)
        self.assertEqual(reag.exp_date, delta.exp_date)
        self.assertEqual(reag.r_type, delta.r_type)
        self.assertEqual(reag.factory, delta.factory)
        self.assertEqual(reag.catalog, delta.catalog)
        self.assertEqual('CREATE', delta.operation)

    def test_update_reagent(self):
        test_post = {
            'size': 'L',
            'vol_cur': 6000,
            'autostainer_sn': 'SN12346'
        }

        client = Client()
        ret = client.put('/reagents/api/reagent/REAG007/',\
            json.dumps(test_post), content_type='application/json')
        
        self.assertEqual(201, ret.status_code)
        self.assertEqual(reag.reagent_sn, 'REAG007')