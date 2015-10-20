from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static
from explorer import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^beaconapi/$', views.beaconApi, name='beaconApi'),
    url(r'^modalapi/$', views.modalApi, name='modalApi'),
    url(r'^precipapi/$', views.precipApi, name='precipApi'),
    url(r'^about/$', views.about, name='about'),
    url(r'^datasources/$', views.datasources, name='datasources'),
    url(r'^criteriascoring/$', views.criteriascoring, name='criteriascoring'),
    url(r'^findingssolutions/$', views.findingssolutions, name='findingssolutions'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
