from django.urls import path

from . import views

urlpatterns  = [
    # /reagents/
    path('', views.index, name='index'),
    # /reagents/1
    #path('<int:id>', views.reagents, name='reagents'),
]