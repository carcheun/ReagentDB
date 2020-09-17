from django.urls import path, include
from rest_framework import routers
from . import views

# define router and register viewsets
# routed to server/reagents/api
router = routers.DefaultRouter()
router.register(r'reagent_view', views.ReagentViewSet)
router.register(r'autostainer', views.AutoStainerStationViewSet)
router.register(r'pa', views.PAViewSet)
router.register(r'padelta', views.PADeltaViewSet)

# actual URL's users should use for POST/GET/PUT
urlpatterns  = [
    # server/reagents/
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    # TODO: authorization to modify 
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('api/reagent/', views.reagent_list),
    path('api/reagent/<str:reagent_sn>/', views.reagent_detail),

    path('test/', views.hello_world, name='test'),
]