import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
from datetime import datetime, time
from dateutil.rrule import rrule, DAILY, YEARLY
from dateutil.relativedelta import relativedelta
from django.db.models import Sum

"""
  Calculates the number of samples that pass and fail in wet and dry weather
"""
class Command(BaseCommand):
	
	def calc_annual_avg_precip(self):
		#between today and 2004
		today = datetime.today()
		earliest = datetime(2003, 1, 1)
		twentySixteen = datetime(2016, 1, 1)

		for dateEval in rrule(YEARLY, dtstart=earliest, until=today):
			mayFirst = dateEval + relativedelta(months=+4)
			augustThirtyFirst = dateEval + relativedelta(months=+8, days=-1)
			avg_daily_precips = []

			for date in rrule(DAILY, dtstart=mayFirst, until=augustThirtyFirst):
				stations = WeatherStations.objects.distinct()
				daily_precips = []
				for station in stations:
					try:
						if date < twentySixteen:
							wd = WeatherData.objects.filter(Station=station, Date=date)[:1]
						else:
							wd = HourlyWeatherData.objects.filter(Station=station, DateTimeUTC=date)[:1]
						for w in wd:
							try:
								daily_precip = float(w.PrecipitationIn)
							except ValueError as e:
								pass
					except WeatherData.DoesNotExist:
						pass

					daily_precips.append(daily_precip)

				try:
					print date
					psum = sum(daily_precips)
					print psum 
					plen = len(daily_precips)
					print plen
					avg_daily_precip = psum / plen
					avg_daily_precips.append(avg_daily_precip)
					
				except TypeError as e:
					print e
					pass


			#write to database
			seasonal_precip = sum(avg_daily_precips)
			updated_values = {'AvgPrecipitationIn': seasonal_precip}
			obj, created = AnnualAvgPrecip.objects.update_or_create(Date=dateEval, defaults=updated_values)




	def handle(self, *args, **options):
		print "Calculating Annual Average Precip Across Weather Stations...."
		self.calc_annual_avg_precip()
		print "Done."





