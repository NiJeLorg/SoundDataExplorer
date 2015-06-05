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
		stations = WeatherStations.objects.distinct()
		#between today and 2004
		today = datetime.today()
		earliest = datetime(2013, 12, 1)

		for dateEval in rrule(MONTHLY, dtstart=earliest, until=today):
			print dateEval.strftime("%Y/%m/%d")

			for counter, station in enumerate(stations):
				#airport station
				if station.Icao:
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

				#personal weather station
				if station.PwsId:
					print station.PwsId
					stringMonth = dateEval.strftime('%m')
					stringYear = dateEval.strftime('%Y')

					#http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=KCTNORWA4&graphspan=month&month=1&year=2014&format=1 
					url = base_url + '/weatherstation/WXDailyHistory.asp?ID=' + station.PwsId + '&graphspan=month&month=' + stringMonth + '&year=' + stringYear + '&format=1'
					response = urllib.urlopen(url)
					datas = response.read()
					datas = datas.replace('<br />', '')
					datas = datas.replace('<br>', '')
					datas = datas.splitlines()
					for data in datas:
						data = data.split(',')
						print data
						if data[0] != '' and data[0] != 'Date':
							wd = WeatherData()
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
		self.get_precip_data()




