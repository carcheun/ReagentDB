import logging

from .models import User
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

logger = logging.getLogger(__name__)

@api_view(['POST'])
def RegisterUser(request):
    """Register new users
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        User.objects.create_user(username=request.data['username'], password=request.data['password'])
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def Logout(request):
    """Delete login token
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    try:
        request.auth.delete()
    except (AttributeError, ObjectDoesNotExist):
        logger.error("Authentication token does not exist!")
    return Response(status=status.HTTP_200_OK)
