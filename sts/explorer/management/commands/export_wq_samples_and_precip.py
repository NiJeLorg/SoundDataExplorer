import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import csv
from datetime import datetime, time
from dateutil.rrule import rrule, DAILY
from dateutil.relativedelta import relativedelta
from django.db.models import Sum

# import settings to point to the media directory
from django.conf import settings


class Command(BaseCommand):
	
	def export_wq_samples_and_precip(self):
		__location__ = settings.MEDIA_ROOT
		with open(os.path.join(__location__, 'documents/wq_samples_and_precip.csv'), 'wb') as f:
			writer = csv.writer(f, quoting=csv.QUOTE_ALL)
			# header row
			headerRow = ['State','County','BeachID','Beach Name', 'Date', 'Sample Value', 'Characteristic Name' 'Precip 48 Hours Prior']
			writer.writerow(headerRow)

			# important dates
			today = datetime.today()
			earliest = datetime(2016, 1, 1)
			twentySixteen = datetime(2016, 1, 1)
			midnight = time(0,0,0)

			# select all beaches
			beaches = Beaches.objects.all()

			for beach in beaches:
				for dateEval in rrule(DAILY, dtstart=earliest, until=today):
					samples = BeachWQSamples.objects.filter(BeachID__exact=beach, StartDate__exact=dateEval)

					NumberOfSamples = len(samples)
					if NumberOfSamples > 0:
						for sample in samples:
							#skip Total Coliform samples
							if sample.CharacteristicName != 'Total Coliform':
								# check if sample date <= 2016 
								# 48 hours prior precip is two days before sample date using WeatherDataPWS and WeatherData tables
								if dateEval < twentySixteen:
									yesterday = sample.StartDate + relativedelta(days=-1)
									twoDaysAgo = sample.StartDate + relativedelta(days=-2)
									oneYearAgo = sample.StartDate + relativedelta(years=-1)

									# check to see if personal weather station data exist for this beach on these days
									pwscount = WeatherDataPWS.objects.filter(Station__BeachID__exact=beach, Date__gte=twoDaysAgo, Date__lte=yesterday).count()
									if pwscount > 0:
										# get the nearest staion with data
										stations = WeatherStationsPWS.objects.filter(BeachID__exact=beach).order_by('DistanceKm')
										used_stations = 0
										for station in stations:

											# check to see if the station has 0 precipitation within the last year -- if so skip this station
											precip_check = WeatherDataPWS.objects.filter(Station__exact=station, Date__gte=oneYearAgo, Date__lte=yesterday).aggregate(Sum('PrecipitationIn'))
											# get count of precip objects excluding any that have a daily value greater than 5 inches and skip if there are none
											precipcount_under5 = WeatherDataPWS.objects.filter(Station__exact=station, Date__gte=twoDaysAgo, Date__lte=yesterday).exclude(PrecipitationIn__gt=5).count()

											if precip_check['PrecipitationIn__sum'] > 0 and precipcount_under5 > 0:
												# pull precip data for next step
												precip = WeatherDataPWS.objects.filter(Station__exact=station, Date__gte=twoDaysAgo, Date__lte=yesterday).aggregate(Sum('PrecipitationIn'))
												used_stations += 1
												break

										if used_stations == 0:
											# fall back to the airport precip data if no personal weather stations with usable data
											precip = WeatherData.objects.filter(Station__BeachID__exact=beach, Date__gte=twoDaysAgo, Date__lte=yesterday).aggregate(Sum('PrecipitationIn'))

									else:
										# fall back to the airport precip data if no personal weather stations nearby
										precip = WeatherData.objects.filter(Station__BeachID__exact=beach, Date__gte=twoDaysAgo, Date__lte=yesterday).aggregate(Sum('PrecipitationIn'))

									fortyEightHourPrecip = precip['PrecipitationIn__sum']

								else:
									# make a date time object from the sample date time in UTC 
									# if time == '00:00:00' then assume sample is taken at 11am Eastern (6am UTC)
									if sample.StartTime == midnight:
										sampleDateTime = datetime.combine(sample.StartDate, time(6,0,0))
									else:
										sampleDateTime = datetime.combine(sample.StartDate, sample.StartTime) + relativedelta(hours=-5)

									fortyEightHoursAgo = sampleDateTime + relativedelta(hours=-48)
									oneYearAgo = sampleDateTime + relativedelta(years=-1)

									# times used for selecting precip data below
									fiftyNineMinutesAgo = sampleDateTime + relativedelta(minutes=-59)
									twentyFourHoursAgo = sampleDateTime + relativedelta(hours=-24)
									twentyFiveHoursAgo = twentyFourHoursAgo + relativedelta(minutes=-59)

									# check to see if personal weather station data exist for this beach on these days
									pwscount = HourlyWeatherDataPWS.objects.filter(Station__BeachID__exact=beach, DateTimeUTC__gte=fortyEightHoursAgo, DateTimeUTC__lte=sampleDateTime).count()
									if pwscount > 0:
										# get the nearest staion with data
										stations = WeatherStationsPWS.objects.filter(BeachID__exact=beach).order_by('DistanceKm')
										used_stations = 0
										for station in stations:

											# check to see if the station has 0 precipitation within the last year -- if so skip this station
											precip_check = HourlyWeatherDataPWS.objects.filter(Station__exact=station, DateTimeUTC__gte=oneYearAgo, DateTimeUTC__lte=sampleDateTime).aggregate(Sum('PrecipitationIn'))
											# get count of precip objects excluding any that have a daily value greater than 5 inches and skip if there are none
											precipcount_under5 = HourlyWeatherDataPWS.objects.filter(Station__exact=station, DateTimeUTC__gte=fortyEightHoursAgo, DateTimeUTC__lte=sampleDateTime).exclude(PrecipitationIn__gt=5).count()

											if precip_check['PrecipitationIn__sum'] > 0 and precipcount_under5 > 0:
												# pull precip data for two time points -- right prior to the sample and 24 hours prior, then sum to get 48 hour cumulative
												precip_sampleDateTime = HourlyWeatherDataPWS.objects.filter(Station__exact=station, DateTimeUTC__gte=fiftyNineMinutesAgo, DateTimeUTC__lte=sampleDateTime).aggregate(Sum('PrecipitationIn'))
												
												precip_twentyFourHoursAgo = HourlyWeatherDataPWS.objects.filter(Station__exact=station, DateTimeUTC__gte=twentyFiveHoursAgo, DateTimeUTC__lte=twentyFourHoursAgo).aggregate(Sum('PrecipitationIn'))

												if precip_sampleDateTime['PrecipitationIn__sum'] is not None and precip_twentyFourHoursAgo['PrecipitationIn__sum'] is not None:
													fortyEightHourPrecip = precip_sampleDateTime['PrecipitationIn__sum'] + precip_twentyFourHoursAgo['PrecipitationIn__sum']
													
													used_stations += 1
													break

										if used_stations == 0:
											# fall back to the airport precip data if no personal weather stations with usable data
											precip_sampleDateTime = HourlyWeatherData.objects.filter(Station__BeachID__exact=beach, DateTimeUTC__gte=fiftyNineMinutesAgo, DateTimeUTC__lte=sampleDateTime).aggregate(Sum('PrecipitationIn'))

											precip_twentyFourHoursAgo = HourlyWeatherData.objects.filter(Station__BeachID__exact=beach, DateTimeUTC__gte=twentyFiveHoursAgo, DateTimeUTC__lte=twentyFourHoursAgo).aggregate(Sum('PrecipitationIn'))

											if precip_sampleDateTime['PrecipitationIn__sum'] is not None and precip_twentyFourHoursAgo['PrecipitationIn__sum'] is not None:
												fortyEightHourPrecip = precip_sampleDateTime['PrecipitationIn__sum'] + precip_twentyFourHoursAgo['PrecipitationIn__sum']
											else:
												fortyEightHourPrecip = 0										


									else:
										# fall back to the airport precip data if no personal weather stations nearby
										precip_sampleDateTime = HourlyWeatherData.objects.filter(Station__BeachID__exact=beach, DateTimeUTC__gte=fiftyNineMinutesAgo, DateTimeUTC__lte=sampleDateTime).aggregate(Sum('PrecipitationIn'))

										precip_twentyFourHoursAgo = HourlyWeatherData.objects.filter(Station__BeachID__exact=beach, DateTimeUTC__gte=twentyFiveHoursAgo, DateTimeUTC__lte=twentyFourHoursAgo).aggregate(Sum('PrecipitationIn'))

										if precip_sampleDateTime['PrecipitationIn__sum'] is not None and precip_twentyFourHoursAgo['PrecipitationIn__sum'] is not None:
											fortyEightHourPrecip = precip_sampleDateTime['PrecipitationIn__sum'] + precip_twentyFourHoursAgo['PrecipitationIn__sum']
										else:
											fortyEightHourPrecip = 0

								#empty list for a row
								row = ['','','','','','','','']
								row[0] = beach.State
								row[1] = beach.County
								row[2] = beach.BeachID
								row[3] = beach.BeachName
								row[4] = dateEval.strftime('%m-%d-%Y')
								row[5] = sample.ResultValue
								row[6] = sample.CharacteristicName
								row[7] = fortyEightHourPrecip

								writer.writerow(row)


	def handle(self, *args, **options):
		print "Export WQ samples and precip data...."
		self.export_wq_samples_and_precip()
		print "Done."




