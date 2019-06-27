import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import csv
from datetime import datetime
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
			#header row
			headerRow = ['State','County','BeachID','Beach Name', 'Date', 'Sample Value', 'Characteristic Name' 'Sample Date Precip', 'Day Before Precip', 'Two Days Before Precip', 'Three Days Before Precip']
			writer.writerow(headerRow)
			beaches = Beaches.objects.all()
			for beach in beaches:
				today = datetime.today()
				earliest = datetime(2016, 1, 1)
				for dateEval in rrule(DAILY, dtstart=earliest, until=today):
					samples = BeachWQSamples.objects.filter(BeachID__exact=beach, StartDate__exact=dateEval)

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
											precip = WeatherDataPWS.objects.filter(Station__exact=station, Date__gte=threeDaysAgo, Date__lte=today).order_by('Date')
											#if there are precip objects then break the for loop
											if len(precip) > 0:
												used_stations += 1
												break

									if used_stations == 0:
										# fall back to the airport precip data if no personal weather stations with usable data
										precip = WeatherData.objects.filter(Station__BeachID__exact=beach, Date__gte=threeDaysAgo, Date__lte=today).order_by('Date')

								else:
									# fall back to the airport precip data if no personal weather stations nearby
									precip = WeatherData.objects.filter(Station__BeachID__exact=beach, Date__gte=threeDaysAgo, Date__lte=today).order_by('Date')


								#empty list for a row
								row = ['','','','','','','','','','','']
								row[0] = beach.State
								row[1] = beach.County
								row[2] = beach.BeachID
								row[3] = beach.BeachName
								row[4] = dateEval.strftime('%m-%d-%Y')
								row[5] = sample.ResultValue
								row[6] = sample.CharacteristicName

								for i,p in enumerate(precip):
									position = i + 7
									row[position] = p.PrecipitationIn


								writer.writerow(row)


	def handle(self, *args, **options):
		print "Export WQ samples and precip data...."
		self.export_wq_samples_and_precip()
		print "Done."




