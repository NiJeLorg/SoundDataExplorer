import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import urllib, string
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY, HOURLY

"""
  Imports historical WU percip data from WU API
"""
class Command(BaseCommand):
	
	def get_precip_data(self):
		#build url to pass to WU
		base_url = "https://api.weather.com/v3/wx/hod/conditions/historical/point"
		beaches = Beaches.objects.all()
		latest = datetime(2018, 10, 31)
		earliest = datetime(2016, 1, 1)

		for dateEval in rrule(DAILY, dtstart=earliest, until=latest):
			#print dateEval.strftime("%Y/%m/%d")
			today = dateEval
			tomorrow = today + relativedelta(hours=23)

			for datetimeEval in rrule(HOURLY, dtstart=today, until=tomorrow):
				print datetimeEval
				begin = datetimeEval
				end = datetimeEval + relativedelta(hours=1)

				for beach in beaches:
					# specified in format “YYYYMMDDHHmm”. 
					startDateTime = begin.strftime('%Y%m%d')

			# for station in stations:
			# 	counter += 1
			# 	print station.Icao
			# 	stringDate = dateEval.strftime('%Y/%m') + '/1'
			# 	#https://api.weather.com/v3/wx/hod/conditions/historical/point?pointType=weighted&geocode=39.86,-104.67&startDateTime=201712071520&endDateTime=201712071520&units=e&format=json&apiKey=yourApiKey 
			# 	url = base_url + 'history/airport/' + station.Icao + '/' + stringDate + '/' +'MonthlyHistory.html?format=1'
			# 	response = urllib.urlopen(url)
			# 	datas = response.read()
			# 	datas = datas.replace('<br />', '')
			# 	datas = datas.replace('<br>', '')
			# 	datas = datas.splitlines()
			# 	for data in datas:
			# 		data = data.split(',')
			# 		if data[0] != '' and data[0] != 'EST' and data[0] != 'EDT':
			# 			wd = WeatherData()
			# 			wd.Station = station
			# 			wd.Date = data[0]
			# 			wd.PrecipitationIn = data[19]
			# 			wd.save()

				#sleep code for 60 seconds ever 200 "API" calls to limit attention to ourselves
				# if counter % 50 == 0:
				# 	print "Sleeping at counter " + str(counter)
				# 	time.sleep(60)


	def handle(self, *args, **options):
		print "Loading Weather.com Historical Data...."
		self.get_precip_data()




