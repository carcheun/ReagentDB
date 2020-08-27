from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

import requests

from . serializers import CreateUserSerializer

CLIENT_ID = 'BvT8SLBI5sjMh3baI3TMKSLJAR7bSh7qwpUore5F'
CLIENT_SECRET = 'bkSD5j3UaqAlmWvdKQqpPbSdMTHRFvSfYWpzOfHT9NbWtEHGqTcd4kYsxW2WBcMcm50RhShQ5Ic8rqcPVCNHshsSQahd5VvjnkJ6T9l3bphCy9Lzs0X8LGmckgIUJ1ow'

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Allow users to register to server, input is
    {'username': 'username', 'password': '12345'}
    """
    # put data from request into serializer
    serializer = CreateUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        r = requests.post('http://localhost:8000/o/token/',
            data={
                'grant_type' : 'password',
                'username' : request.data['username'],
                'password' : request.data['password'],
                'client_id' : CLIENT_ID,
                'client_secret' : CLIENT_SECRET,
            },
        )
        return Response(r.json())
    return Response(serializer.errors)

@api_view(['POST'])
@permission_classes([AllowAny])
def token(request):
    """
    Gets tokens with username and password
    {'username': 'username', 'password': '12345'}
    """
    r = requests.post('http://localhost:8000/o/token/',
        data={
            'grant_type': 'password',
            'username': request.data['username'],
            'password': request.data['password'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
    )
    return Response(r.json())

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    refresh our expiring tokens
    {'refresh_token': '<token>'}
    """
    r = requests.post('http://localhost:8000/o/token/',
        data={
            'grant_type': 'refresh_token',
            'refresh_token': request.data['refresh_token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
    )
    return Response(r.json())

@api_view(['POST'])
@permission_classes([AllowAny])
def revoke_token(request):
    """
    Revoke a token
    {'token' : '<token>'}
    """

    r = requests.post('http://localhost:8000/o/token/',
        data={
            'token': request.data['token'],
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
        },
    )
    if r.status_code == requests.codes.ok:
        return Response({'message': 'token revoked'}, r.status_code)

    return Response(r.json(), r.status_code)