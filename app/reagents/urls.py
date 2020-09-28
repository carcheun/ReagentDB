from django.urls import path, include
from rest_framework import routers
from . import views, views_reagents

# define router and register viewsets
# routed to server/reagents/api
router = routers.DefaultRouter()
router.register(r'reagent', views_reagents.ReagentViewSet)
router.register(r'autostainer', views.AutoStainerStationViewSet)
router.register(r'pa', views.PAViewSet)
router.register(r'padelta', views.PADeltaViewSet)
router.register(r'reagentdelta', views_reagents.ReagentDeltaViewSet)

# actual URL's users should use for POST/GET/PUT
urlpatterns  = [
    # server/reagents/
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    # TODO: authorization to modify 
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('test/', views.hello_world, name='test'),
]