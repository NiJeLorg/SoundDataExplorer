from django.conf.urls import patterns, include, url
from explorer import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^beaconapi/$', views.beaconApi, name='beaconApi'),
    url(r'^modalapi/$', views.modalApi, name='modalApi'),
    url(r'^precipapi/$', views.precipApi, name='precipApi'),
    url(r'^about/$', views.about, name='about'),
    url(r'^datasources/$', views.datasources, name='datasources'),
    url(r'^criteriascoring/$', views.criteriascoring, name='criteriascoring'),
    url(r'^findingssolutions/$', views.findingssolutions, name='findingssolutions'),
)
