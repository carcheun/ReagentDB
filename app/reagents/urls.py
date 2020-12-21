from django.urls import path, include
from rest_framework import routers
from . import views_pa, views_reagents

# define router and register viewsets
# routed to server/reagents/api
router = routers.DefaultRouter()
router.register(r'reagent', views_reagents.ReagentViewSet)
router.register(r'autostainer', views_pa.AutoStainerStationViewSet)
router.register(r'pa', views_pa.PAViewSet)
router.register(r'padelta', views_pa.PADeltaViewSet)
router.register(r'reagentdelta', views_reagents.ReagentDeltaViewSet)

# actual URL's users should use for POST/GET/PUT
urlpatterns  = [
    # server/reagents
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]