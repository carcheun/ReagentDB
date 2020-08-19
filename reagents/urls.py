from django.urls import path, include
from rest_framework import routers
from . import views

# define router and register viewsets
# routed to server/reagents/api
router = routers.DefaultRouter()
router.register(r'reagents', views.ReagentViewSet)
router.register(r'autostainer', views.AutoStainerStationViewSet)
router.register(r'pa', views.PAViewSet)

# actual URL's users should use for POST/GET/PUT
urlpatterns  = [
    # server/reagents/
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    # TODO: authorization to modify
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/reagent_list/', views.reagent_list),
    path('api/reagent_list/<int:id>/', views.reagent_detail),
    path('api/pa_list/', views.pa_list),
    path('api/pa_list/<str:catalog>/', views.pa_detail),
    path('test/', views.hello_world, name='test'),
]