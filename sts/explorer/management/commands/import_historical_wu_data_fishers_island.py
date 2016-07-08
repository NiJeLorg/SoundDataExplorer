import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import urllib, string
import time
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY

"""
  Imports historical WU percip data from WU API
"""
class Command(BaseCommand):
	
	def get_precip_data(self):
		#build url to pass to WU
		base_url = "http://www.wunderground.com/";
		stations = WeatherStations.objects.filter(id__in=[1394,1395,1396,1397])
		#between today and 2004
		today = datetime.today()
		earliest = datetime(2004, 1, 1)
		counter = 0

		for dateEval in rrule(MONTHLY, dtstart=earliest, until=today):
			print dateEval.strftime("%Y/%m/%d")

			for station in stations:
				counter += 1
				print station.Icao
				stringDate = dateEval.strftime('%Y/%m') + '/1'
				#http://www.wunderground.com/history/airport/KBDR/2014/1/1/MonthlyHistory.html?format=1 
				url = base_url + 'history/airport/' + station.Icao + '/' + stringDate + '/' +'MonthlyHistory.html?format=1'
				response = urllib.urlopen(url)
				datas = response.read()
				datas = datas.replace('<br />', '')
				datas = datas.replace('<br>', '')
				datas = datas.splitlines()
				for data in datas:
					data = data.split(',')
					if data[0] != '' and data[0] != 'EST' and data[0] != 'EDT':
						wd = WeatherData()
						wd.Station = station
						wd.Date = data[0]
						wd.PrecipitationIn = data[19]
						wd.save()

				#sleep code for 60 seconds ever 200 "API" calls to limit attention to ourselves
				if counter % 50 == 0:
					print "Sleeping at counter " + str(counter)
					time.sleep(60)


	def handle(self, *args, **options):
		print "Loading WU Precip Data...."
		self.get_precip_data()




