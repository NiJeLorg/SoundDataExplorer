import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
from datetime import datetime
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta
from django.db.models import Sum

"""
  Calculates the number of samples that pass, number of dry samples that pass, and number of wet samples that pass
"""
class Command(BaseCommand):
	
	def calc_pass_fail(self):
		#between today and 2004
		today = datetime.today()
		earliest = datetime(2003, 1, 1)

		for dateEval in rrule(MONTHLY, dtstart=earliest, until=today):
			firstOfMonth = dateEval
			lastOfMonth = dateEval + relativedelta(months=+1, days=-1)
			# loop through Beaches and see if any samples exist for that beach between these dates
			beaches = Beaches.objects.all()
			for beach in beaches:
				NumberOfSamples = 0
				TotalNumberOfSamples = 0
				TotalPassSamples = 0
				TotalDryWeatherSamples = 0
				DryWeatherPassSamples = 0
				TotalWetWeatherSamples = 0
				WetWeatherPassSamples = 0
				samples = BeachWQSamples.objects.filter(BeachID__exact=beach, StartDate__gte=firstOfMonth, StartDate__lte=lastOfMonth)
				NumberOfSamples = len(samples)
				if NumberOfSamples > 0:
					for sample in samples:
						#skip Total Coliform samples
						if sample.CharacteristicName != 'Total Coliform':
							today = sample.StartDate
							threeDaysAgo = sample.StartDate + relativedelta(days=-3)

							# check to see if personal weather station data exist for this beach on these days
							pwscount = WeatherDataPWS.objects.filter(Station__BeachID__exact=beach, Date__gte=threeDaysAgo, Date__lte=today).count()
							if pwscount > 0:
								# get the nearest staion with data
								stations = WeatherStationsPWS.objects.filter(BeachID__exact=beach).order_by('DistanceKm')
								for station in stations:
									# get count of precip objects
									precipcount = WeatherDataPWS.objects.filter(Station__exact=station, Date__gte=threeDaysAgo, Date__lte=today).count()
									# pull precip data for next step
									precip = WeatherDataPWS.objects.filter(Station__exact=station, Date__gte=threeDaysAgo, Date__lte=today).aggregate(Sum('PrecipitationIn'))
									#if there are precip objects, then break the for loop
									if precipcount > 0:
										print station
										print sample.BeachID
										print precip['PrecipitationIn__sum']
										break

							else:
								# fall back to the airport precip data if no personal weather stations nearby
								precip = WeatherData.objects.filter(Station__BeachID__exact=beach, Date__gte=threeDaysAgo, Date__lte=today).aggregate(Sum('PrecipitationIn'))
								print sample.BeachID
								print precip['PrecipitationIn__sum']

							# do some counting
							if precip['PrecipitationIn__sum'] > 0.5:
								TotalWetWeatherSamples += 1
								TotalNumberOfSamples += 1
							else:
								TotalDryWeatherSamples += 1 
								TotalNumberOfSamples += 1

							if sample.CharacteristicName == 'Enterococcus':
								if sample.ResultValue <= 104:
									TotalPassSamples += 1
									if precip['PrecipitationIn__sum'] > 0.5:
										WetWeatherPassSamples += 1
									else:
										DryWeatherPassSamples += 1

							elif sample.CharacteristicName == 'Fecal Coliform':
								if sample.ResultValue <= 1000:
									TotalPassSamples += 1
									if precip['PrecipitationIn__sum'] > 0.5:
										WetWeatherPassSamples += 1
									else:
										DryWeatherPassSamples += 1

				# write to database
				updated_values = {'NumberOfSamples': TotalNumberOfSamples, 'TotalPassSamples': TotalPassSamples, 'TotalDryWeatherSamples': TotalDryWeatherSamples, 'DryWeatherPassSamples': DryWeatherPassSamples, 'TotalWetWeatherSamples': TotalWetWeatherSamples, 'WetWeatherPassSamples': WetWeatherPassSamples}

				obj, created = MonthlyScores.objects.update_or_create(BeachID=beach, MonthYear=firstOfMonth, defaults=updated_values)

	def handle(self, *args, **options):
		print "Calculating Monthly Sample Pass/Fail...."
		self.calc_pass_fail()
		print "Done."




