import json
from datetime import datetime
from django.db import models
from django.test import TestCase, Client
from django.forms.models import model_to_dict

from .models import PA, AutoStainerStation, PADelta, Reagent, ReagentDelta

# Create your tests here.
class PASyncClientSyncTests(TestCase):
    fixtures = ['test_set_A_autostainerstation.json', 'test_pa_set_A.json.json', \
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

    def test_unlock_reagent(self):''
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
        
        reag = Reagent.objects.get(reagent_sn='REAG001')
        self.assertFalse(reag.in_use)

    def test_scan_reagent(self):
        #Check scanned reagent
        #TODO: please find out scanned data from reagent scanning

        return

    def test_valid_reagents(self):
        #Returned reagents are all above 150ul and not expired
        client = Client()
        ret = client.get('/reagents/api/reagent/valid_reagents/')
        # should have 1 missing sample
        reags = reagent.objects.all()
        self.assertEqual(reag.length - 1, ret.length)


    def test_decrease_volume(self):
        # decrease volume and check
        reagent_sn = 'REAG002'
        dec_vol = 250

        client = Client()
        reag = Reagent.objects.get(reagent_sn=reagent_sn)
        cur_vol = reag.cur_vol

        test_post = {
            'dec_vol': dec_vol,
            'autostainer_sn': 'STAINER0001'
        }

        response = client.put('/reagents/api/reagent/' + reagent_sn + '/decrease_volume/',\
            json.dumps(test_post), content_type='application/json')
        reag = Reagent.objects.get(reagent_sn=reagent_sn)
        
        self.assertEqual(cur_vol - dec_vol, reag.cur_vol)

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

        response = client.put('/reagents/api/reagent/' + reagent_sn + '/decrease_volume/',\
            json.dumps(test_post), content_type='application/json')
        reag = Reagent.objects.get(reagent_sn=reagent_sn)
        
        self.assertEqual(0, reag.cur_vol)

