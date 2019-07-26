import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
from datetime import datetime, time
from dateutil.rrule import rrule, DAILY
from dateutil.relativedelta import relativedelta
from django.db.models import Sum

"""
  Calculates the number of samples that pass and fail in wet and dry weather
"""
class Command(BaseCommand):
	
	def calc_daily_avg_precip(self):
		#between today and 2004
		today = datetime.today()
		earliest = datetime(2003, 1, 1)
		twentySixteen = datetime(2016, 1, 1)
		midnight = time(0,0,0)

		for date in rrule(DAILY, dtstart=earliest, until=today):
			stations = WeatherStations.objects.distinct()
			daily_precips = []
			for station in stations:
				try: 
					wd = WeatherData.objects.filter(Station=station, Date=date)[:1]
					for w in wd:
						try:
							daily_precip = float(w.PrecipitationIn)
						except ValueError as e:
							daily_precip = None
				except WeatherData.DoesNotExist:
					daily_precip = None

				daily_precips.append(daily_precip)

			try:
				avg_precip = sum(daily_precips) / float(len(daily_precips))
				#write to database
				updated_values = {'AvgPrecipitationIn': avg_precip}
				print date
				obj, created = DailyAvgPrecip.objects.update_or_create(Date=date, defaults=updated_values)
			except TypeError as e:
				pass



	def handle(self, *args, **options):
		print "Calculating Daily Average Precip Across Weather Stations...."
		self.calc_daily_avg_precip()
		print "Done."




