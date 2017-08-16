import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import urllib, json
import time


"""
  Finds nearest weather station from WU API
"""
class Command(BaseCommand):
	
	def weather_station_lookup(self):
		#build url to pass to WU
		key = '1b508ea9e71ea36f'
		base_url = "http://api.wunderground.com/api/" + key + "/geolookup/q/";
		beaches = Beaches.objects.filter(id__in=[1887])
		for counter, beach in enumerate(beaches):
			lat = beach.StartLatitude
			lon = beach.StartLongitude
			url = base_url + str(lat) + ',' + str(lon) + '.json'
			response = urllib.urlopen(url)
			data = json.loads(response.read())

			airportStations = data['location']['nearby_weather_stations']['airport']['station']
			# no longer including personal weather stations
			#pwsStations = data['location']['nearby_weather_stations']['pws']['station']
			for i, airport in enumerate(airportStations):
				if i == 0:
					ws = WeatherStations()
					ws.BeachID = beach
					ws.City = airport['city']
					ws.State = airport['state']
					ws.Country = airport['country']
					ws.Icao = airport['icao']
					ws.Lat = float(airport['lat'])
					ws.Lon = float(airport['lon'])
					ws.save()


			#for j, pws in enumerate(pwsStations):
			#	if j <= 2:
			#		ws = WeatherStations()
			#		ws.BeachID = beach
			#		ws.Neighborhood = pws['neighborhood']
			#		ws.City = pws['city']
			#		ws.State = pws['state']
			#		ws.Country = pws['country']
			#		ws.PwsId = pws['id']
			#		ws.DistanceKm = int(pws['distance_km'])
			#		ws.DistanceMi = int(pws['distance_mi'])
			#		ws.save()

			#sleep code for 1 minute to conform with API
			if counter % 10 == 0:
				print "Sleeping at counter " + str(counter)
				time.sleep(60)


	def handle(self, *args, **options):
		print "Loading WU Metadata...."
		self.weather_station_lookup()
		print "Done."




