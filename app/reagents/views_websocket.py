from rest_framework.parsers import JSONParser
from django.shortcuts import render

def index(request):
    return render(request, 'reagents/index.html')

"""
display status
display inventory ?

"""