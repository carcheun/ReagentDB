from django.urls import path, include
from rest_framework import routers
from . import views

# define router and register viewsets
# routed to server/reagents/api
router = routers.DefaultRouter()
router.register(r'reagent_view', views.ReagentViewSet)
router.register(r'autostainer_view', views.AutoStainerStationViewSet)
router.register(r'pa_view', views.PAViewSet)

# actual URL's users should use for POST/GET/PUT
urlpatterns  = [
    # server/reagents/
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    # TODO: authorization to modify 
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    path('api/reagent/', views.reagent_list),
    path('api/reagent/<str:reagent_sn>/', views.reagent_detail),
    
    path('api/pa/', views.pa_list),
    path('api/pa/<str:catalog>/', views.pa_detail),
    path('api/sync/pa/', views.pa_recieve_sync),

    path('api/autostainer/', views.autostainerstation_list),
    path('api/autostainer/<str:sn>/', views.autostainerstation_detail),
    path('api/autostainer/<str:sn>/reagents/', views.autostainer_get_reagents),
    # TODO: a path to call to sync what the autostainer registered and
    # then update (?)
    path('api/autostainer/<str:sn>/reagents/sync/', views.autostainer_get_reagents),

    path('test/', views.hello_world, name='test'),
]