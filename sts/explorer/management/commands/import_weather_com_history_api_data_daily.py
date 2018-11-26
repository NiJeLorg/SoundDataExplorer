import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import urllib, json
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY

# import settings for the API key
from django.conf import settings

"""
  Imports historical weather data from the weather.com history on demand API
"""
class Command(BaseCommand):
	
	def get_precip_data_airport(self):
		#build url to pass to WU
		base_url = "https://api.weather.com/v3/wx/hod/conditions/historical/point"
		stations = WeatherStations.objects.all()
		latest = datetime(2018, 10, 31)
		earliest = datetime(2017, 1, 1)
		counter = 0

		for dateEval in rrule(DAILY, dtstart=earliest, until=latest):
			print dateEval.strftime("%Y/%m/%d")

			for station in stations:
				counter += 1
				print station.Icao

				try:
					# specified in format 'YYYYMMDDHHmm'
					stringToday = dateEval.strftime('%Y%m%d%H%M')
					#https://api.weather.com/v3/wx/hod/conditions/historical/point?pointType=weighted&geocode=39.86,-104.67&startDateTime=201712071520&endDateTime=201712071520&units=e&format=json&apiKey=yourApiKey 
					url = base_url + '?pointType=weighted&geocode=' + station.Lat + ',' + station.Lon + '&startDateTime=' + stringToday + '&endDateTime=' + stringToday + '&units=e&format=json&apiKey=' + settings.WEATHER_API_KEY

					response = urllib.urlopen(url)
					data = json.loads(response.read())

					wd = WeatherData()
					wd.Station = station
					wd.Date = dateEval
					wd.PrecipitationIn = data['precip24Hour']
					wd.save()				

				except Exception as e:
					print e
					time.sleep(60)
					pass


				#sleep code for 6 seconds every 100 API calls to keep from exceeding bandwidth
				if counter % 100 == 0:
					print "Sleeping at counter " + str(counter)
					time.sleep(6)

	def get_precip_data_pws(self):
		#build url to pass to WU
		base_url = "https://api.weather.com/v3/wx/hod/conditions/historical/point"
		stations = WeatherStationsPWS.objects.all()
		latest = datetime(2018, 10, 31)
		earliest = datetime(2017, 1, 1)
		counter = 0

		for dateEval in rrule(DAILY, dtstart=earliest, until=latest):
			print dateEval.strftime("%Y/%m/%d")

			for station in stations:
				print station.BeachID
				counter += 1

				try:
					# specified in format 'YYYYMMDDHHmm'
					stringToday = dateEval.strftime('%Y%m%d%H%M')
					#https://api.weather.com/v3/wx/hod/conditions/historical/point?pointType=weighted&geocode=39.86,-104.67&startDateTime=201712071520&endDateTime=201712071520&units=e&format=json&apiKey=yourApiKey 
					url = base_url + '?pointType=weighted&geocode=' + str(station.BeachID.StartLatitude) + ',' + str(station.BeachID.StartLongitude) + '&startDateTime=' + stringToday + '&endDateTime=' + stringToday + '&units=e&format=json&apiKey=' + settings.WEATHER_API_KEY

					response = urllib.urlopen(url)
					data = json.loads(response.read())

					wd = WeatherDataPWS()
					wd.Station = station
					wd.Date = dateEval
					wd.PrecipitationIn = data['precip24Hour']
					wd.save()

				except Exception as e:
					print e
					time.sleep(60)
					pass


				#sleep code for 6 seconds every 100 API calls to keep from exceeding bandwidth
				if counter % 100 == 0:
					print "Sleeping at counter " + str(counter)
					time.sleep(6)


	def handle(self, *args, **options):
		print "Loading Daily Weather.com Historical Data for local Airports...."
		self.get_precip_data_airport()
		print "Loading Daily Weather.com Historical Data for local PWS...."
		self.get_precip_data_pws()





