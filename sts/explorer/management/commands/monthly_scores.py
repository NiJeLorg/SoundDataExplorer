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
							oneYearAgo = sample.StartDate + relativedelta(years=-1)

							# check to see if personal weather station data exist for this beach on these days
							pwscount = WeatherDataPWS.objects.filter(Station__BeachID__exact=beach, Date__gte=threeDaysAgo, Date__lte=today).count()
							if pwscount > 0:
								# get the nearest staion with data
								stations = WeatherStationsPWS.objects.filter(BeachID__exact=beach).order_by('DistanceKm')
								used_stations = 0
								for station in stations:

									# check to see if the station has 0 precipitation within the last year -- if so skip this station
									precip_check = WeatherDataPWS.objects.filter(Station__exact=station, Date__gte=oneYearAgo, Date__lte=today).aggregate(Sum('PrecipitationIn'))
									# get count of precip objects excluding any that have a daily value greater than 5 inches and skip if there are none
									precipcount_under5 = WeatherDataPWS.objects.filter(Station__exact=station, Date__gte=threeDaysAgo, Date__lte=today).exclude(PrecipitationIn__gt=5).count()

									if precip_check['PrecipitationIn__sum'] > 0 and precipcount_under5 > 0:
										# pull precip data for next step
										precip = WeatherDataPWS.objects.filter(Station__exact=station, Date__gte=threeDaysAgo, Date__lte=today).aggregate(Sum('PrecipitationIn'))
										#if there are precip objects and the sum of precip is > 0, then break the for loop
										if precip['PrecipitationIn__sum'] is not None:
											used_stations += 1
											print station
											print sample.BeachID
											print precip['PrecipitationIn__sum']
											break

								if used_stations == 0:
									# fall back to the airport precip data if no personal weather stations with usable data
									precip = WeatherData.objects.filter(Station__BeachID__exact=beach, Date__gte=threeDaysAgo, Date__lte=today).aggregate(Sum('PrecipitationIn'))
									print sample.BeachID
									print precip['PrecipitationIn__sum']

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




