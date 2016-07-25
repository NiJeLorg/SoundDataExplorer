from django.conf.urls import include, url
from explorer import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^beaconapi/$', views.beaconApi, name='beaconApi'),
    url(r'^modalapi/$', views.modalApi, name='modalApi'),
    url(r'^precipapi/$', views.precipApi, name='precipApi'),
]
