from django.contrib import admin

# Register your models here.
from explorer.models import *

admin.site.register(Beaches)
admin.site.register(BeachWQSamples)
admin.site.register(WeatherStations)
admin.site.register(WeatherData)
admin.site.register(MonthlyScores)
