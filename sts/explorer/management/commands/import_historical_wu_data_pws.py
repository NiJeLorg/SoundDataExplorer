import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import urllib, string
import time
from datetime import datetime
from dateutil.rrule import rrule, YEARLY

"""
  Imports historical WU percip data from WU API
"""
class Command(BaseCommand):
	
	def get_precip_data_pws(self):
		#build url to pass to WU
		base_url = "http://www.wunderground.com/";
		stations = WeatherStationsPWS.objects.all()
		#between today and 2004
		today = datetime.today()
		earliest = datetime(2015, 1, 1)
		counter = 0

		for dateEval in rrule(YEARLY, dtstart=earliest, until=today):
			print dateEval.strftime("%Y/%m/%d")

			for station in stations:
				counter += 1

				#personal weather station
				print station.PwsId
				stringMonth = dateEval.strftime('%m')
				stringYear = dateEval.strftime('%Y')

				#http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=KCTNORWA4&graphspan=month&month=1&year=2014&format=1 
				url = base_url + '/weatherstation/WXDailyHistory.asp?ID=' + station.PwsId + '&graphspan=year&year=' + stringYear + '&format=1'
				response = urllib.urlopen(url)
				datas = response.read()
				datas = datas.replace('<br />', '')
				datas = datas.replace('<br>', '')
				datas = datas.splitlines()
				for data in datas:
					data = data.split(',')
					print data
					if data[0] != '' and data[0] != 'Date':
						wd = WeatherDataPWS()
						wd.Station = station
						wd.Date = data[0]
						wd.PrecipitationIn = data[15]
						wd.save()


				#sleep code for 60 seconds ever 200 "API" calls to limit attention to ourselves
				if counter % 50 == 0:
					print "Sleeping at counter " + str(counter)
					time.sleep(60)


	def handle(self, *args, **options):
		print "Loading WU Precip Data...."
		self.get_precip_data_pws()




