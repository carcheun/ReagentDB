from django.urls import path, include
from rest_framework import routers
from . import views

# define router and register viewsets
router = routers.DefaultRouter()
router.register(r'reagents', views.ReagentViewSet)
router.register(r'autostainer', views.AutoStainerStation)

urlpatterns  = [
    # /reagents/
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]