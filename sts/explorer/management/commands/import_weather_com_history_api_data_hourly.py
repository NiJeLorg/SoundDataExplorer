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
	
	def get_precip_data_airport(self, date):
		#build url to pass to WU
		base_url = "https://api.weather.com/v3/wx/hod/conditions/historical/point"
		stations = WeatherStations.objects.all()
		latest = datetime(date, 9, 30, 0, 0)
		earliest = datetime(date, 5, 1, 0, 0)
		counter = 0

		for dateEval in rrule(DAILY, dtstart=earliest, until=latest):
			print dateEval.strftime("%Y%m%d%H%M")

			for station in stations:
				counter += 1
				print station.Icao

				try:
					# specified in format 'YYYYMMDDHHmm'
					stringStartDateTime = dateEval.strftime('%Y%m%d%H%M')
					EndDateTime = dateEval + relativedelta(hours=24, minutes=-1)
					stringEndDateTime = EndDateTime.strftime('%Y%m%d%H%M')
					#https://api.weather.com/v3/wx/hod/conditions/historical/point?pointType=weighted&geocode=39.86,-104.67&startDateTime=201712071520&endDateTime=201712071520&units=e&format=json&apiKey=yourApiKey 
					url = base_url + '?pointType=weighted&geocode=' + station.Lat + ',' + station.Lon + '&startDateTime=' + stringStartDateTime + '&endDateTime=' + stringEndDateTime + '&units=e&format=json&apiKey=' + settings.WEATHER_API_KEY

					response = urllib.urlopen(url)
					data = json.loads(response.read())

					for i, precip in enumerate(data['precip24Hour']):
						wd = HourlyWeatherData()
						wd.Station = station
						wd.DateTimeUTC = dateEval + relativedelta(hours=i)
						wd.PrecipitationIn = precip
						wd.save()				

				except Exception as e:
					print e
					time.sleep(60)
					pass


				#sleep code for 6 seconds every 100 API calls to keep from exceeding bandwidth
				if counter % 100 == 0:
					print "Sleeping at counter " + str(counter)
					time.sleep(6)

	def get_precip_data_pws(self, date):
		#build url to pass to WU
		base_url = "https://api.weather.com/v3/wx/hod/conditions/historical/point"
		stations = WeatherStationsPWS.objects.all()
		latest = datetime(date, 9, 30, 0, 0)
		earliest = datetime(date, 5, 1, 0, 0)
		counter = 0

		for dateEval in rrule(DAILY, dtstart=earliest, until=latest):
			print dateEval.strftime("%Y%m%d%H%M")

			for station in stations:
				counter += 1
				print station.BeachID

				try:
					# specified in format 'YYYYMMDDHHmm'
					stringStartDateTime = dateEval.strftime('%Y%m%d%H%M')
					EndDateTime = dateEval + relativedelta(hours=24, minutes=-1)
					stringEndDateTime = EndDateTime.strftime('%Y%m%d%H%M')
					#https://api.weather.com/v3/wx/hod/conditions/historical/point?pointType=weighted&geocode=39.86,-104.67&startDateTime=201712071520&endDateTime=201712071520&units=e&format=json&apiKey=yourApiKey 
					url = base_url + '?pointType=weighted&geocode=' + str(station.BeachID.StartLatitude) + ',' + str(station.BeachID.StartLongitude) + '&startDateTime=' + stringStartDateTime + '&endDateTime=' + stringEndDateTime + '&units=e&format=json&apiKey=' + settings.WEATHER_API_KEY

					response = urllib.urlopen(url)
					data = json.loads(response.read())

					for i, precip in enumerate(data['precip24Hour']):	
						wd = HourlyWeatherDataPWS()
						wd.Station = station
						wd.DateTimeUTC = dateEval + relativedelta(hours=i)
						wd.PrecipitationIn = precip
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
		# self.get_precip_data_airport(2016)
		# self.get_precip_data_airport(2017)
		# self.get_precip_data_airport(2018)
		print "Loading Daily Weather.com Historical Data for local PWS...."
		self.get_precip_data_pws(2016)
		# self.get_precip_data_pws(2017)
		# self.get_precip_data_pws(2018)
		print "Done."





