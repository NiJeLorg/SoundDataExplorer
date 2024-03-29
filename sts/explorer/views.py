from django.shortcuts import render
from django.http import JsonResponse

# import all azcase_admin models
from explorer.models import *

#for creating json objects
import json

# for date parsing
from datetime import datetime, date, time
import dateutil.parser
from dateutil.relativedelta import relativedelta

# Sum
from django.db.models import Sum, Min, Max, Avg, Count

#using scipy to calculae geomean
from scipy.stats import gmean

#for csv tools
import csv

# path to media root for adding a CSV file 
import os
from django.conf import settings
MEDIA_ROOT = settings.MEDIA_ROOT

from django.db import connection


# Create your views here.
def index(request):	
	tab = "timeline"

	beachId = request.GET.get("beach","")

	endDate = date(2018, 12, 31)
	startDate = endDate + relativedelta(years=-1, days=+1)

	try:
		beach = Beaches.objects.get(BeachID__exact=beachId)
	except Exception, e:
		beach = None

	#select the monthly scores for this beach in the dates requested
	scores = AnnualScores.objects.filter(Year__range=[startDate,endDate])

	# pull average precip by year 
	avg_precips = AnnualAvgPrecip.objects.filter(Date__range=[date(2004,1,1),endDate])

	return render(request, 'explorer/index.html', {'scores':scores, 'startDate':startDate, 'endDate':endDate, 'tab':tab, 'beachId':beachId, 'beach':beach, 'avg_precips':avg_precips})

def beaconApi(request):
	response = {}
	response['type'] = "FeatureCollection"
	response['features'] = []

	startDate = request.GET.get("startDate","2000-01-01")
	endDate = request.GET.get("endDate","2100-01-01")
	# create data objects from start and end dates
	startDateparsed = dateutil.parser.parse(startDate)
	startDateobject = startDateparsed.date()
	endDateparsed = dateutil.parser.parse(endDate)
	endDateobject = endDateparsed.date()

	if startDateobject >= endDateobject:
		endDateobject = startDateobject + relativedelta(years=+1, days=-1)

	#select all the beaches and loop through them
	beaches = Beaches.objects.all()
	for beach in beaches:
		# for certain BeachID, set end data to last day of sampling regardless of what end data the user chose
		if beach.BeachID == 'CT303091':
			# set end date to last day of year for last season
			endDatefilter = date(2012, 12, 31)
		else:
			endDatefilter = endDateobject

		#pull data based on date range selected
		scores = AnnualScores.objects.filter(Year__range=[startDateobject,endDatefilter],BeachID__exact=beach)

		alltimesamples = AnnualScores.objects.filter(BeachID__exact=beach).aggregate(Sum('NumberOfSamples'))
		minMaxDate = BeachWQSamples.objects.filter(BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").aggregate(Min('StartDate'), Max('StartDate'))

		# pull beach stories 
		story = {}
		story['url'] = ''
		beachStory = BeachStoryPage.objects.filter(beach__exact=beach).live().public()
		for bs in beachStory:
			story['url'] = bs.url
			


		for score in scores:
			if score.NumberOfSamples >= 0:
				# parse dates into strings
				data = {}
				data['type'] = 'Feature'
				data['properties'] = {}
				data['properties']['BeachID'] = beach.BeachID
				data['properties']['BeachName'] = beach.BeachName
				data['properties']['State'] = beach.State
				data['properties']['County'] = beach.County
				data['properties']['StartDate'] = minMaxDate['StartDate__min']
				data['properties']['EndDate'] = minMaxDate['StartDate__max']
				data['properties']['AllTimeNumberOfSamples'] = alltimesamples['NumberOfSamples__sum']
				data['properties']['NumberOfSamples'] = score.NumberOfSamples
				data['properties']['TotalPassSamples'] = score.TotalPassSamples
				data['properties']['TotalDryWeatherSamples'] = score.TotalDryWeatherSamples
				data['properties']['DryWeatherPassSamples'] = score.DryWeatherPassSamples
				data['properties']['TotalWetWeatherSamples'] = score.TotalWetWeatherSamples
				data['properties']['WetWeatherPassSamples'] = score.WetWeatherPassSamples
				data['properties']['MaxValueWet'] = score.MaxValueWet
				data['properties']['MaxValueDry'] = score.MaxValueDry
				data['properties']['BeachStory'] = story['url']
				data['geometry'] = {}
				data['geometry']['type'] = 'Point'
				# average the start and end lat lons
				if beach.EndLongitude:
					lon = (float(beach.StartLongitude) + float(beach.EndLongitude)) / 2
				else:
					lon = float(beach.StartLongitude)

				if beach.EndLatitude:
					lat = (float(beach.StartLatitude) + float(beach.EndLatitude)) / 2
				else:
					lat = float(beach.StartLatitude)
					
				data['geometry']['coordinates'] = [lon, lat]
				response['features'].append(data)



	return JsonResponse(response)


def modalApi(request):

	startDate = request.GET.get("startDate","2000-01-01")
	endDate = request.GET.get("endDate","2100-01-01")
	beachId = request.GET.get("beachId","")
	tab = request.GET.get("tab","precip")
	twentySixteen = date(2016, 1, 1)
	midnight = time(0,0,0)

	#setup for CSV files
	ts = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
	folder = "/csv_files/"+ beachId +"/"
	filename_all = "SoundHealthExplorer_download_all_"+ beachId +".csv"
	filename_filtered = "SoundHealthExplorer_download_filtered_"+ beachId +"_"+ ts +".csv"

	if not os.path.exists(MEDIA_ROOT + folder):
		os.makedirs(MEDIA_ROOT + folder)

	# create data objects from start and end dates
	startDateparsed = dateutil.parser.parse(startDate)
	startDateobject = startDateparsed.date()
	endDateparsed = dateutil.parser.parse(endDate)
	endDateplusone = endDateparsed.date()
	endDateobject = endDateplusone + relativedelta(days=-1)

	if startDateobject >= endDateobject:
		endDateobject = startDateobject + relativedelta(years=+1, days=-1)


	#beach look up
	beach = Beaches.objects.get(BeachID__exact=beachId)

	# pull beach stories 
	story = {}
	story['url'] = ''
	beachStory = BeachStoryPage.objects.filter(beach__exact=beach).live().public()
	for bs in beachStory:
		story['url'] = bs.url	

	#select the annual scores for this beach in the dates requested
	scores = AnnualScores.objects.filter(Year__range=[startDateobject,endDateobject],BeachID__exact=beach)

	#list of values to calulate gmean
	sampleList = []

	# select all samples in the range
	samples = BeachWQSamples.objects.filter(StartDate__range=[startDateobject,endDateobject],BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").order_by('StartDate')

	# write to CSV file as we're making the query
	filtered_csv_path = os.path.join(MEDIA_ROOT + folder + filename_filtered)
	with open(filtered_csv_path, 'wb') as f:
		writer = csv.writer(f, quoting=csv.QUOTE_ALL)
		headerRow = ['Beach ID','Beach Name', 'Station ID', 'Station Name', 'State Code', 'County Name', 'Sample Date', 'Result Value', 'Result Measure Unit', 'Characteristic Name', 'Precipitation (In.)']
		writer.writerow(headerRow)

		NumberOfSamples = len(samples)
		if NumberOfSamples > 0:
			for sample in samples:
				if sample.StartDate < twentySixteen:
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


				sample.precipSum = fortyEightHourPrecip

				# make list of sample values for gmean
				# exclude Fecal Coliform from geomean
				if sample.CharacteristicName != "Fecal Coliform":
					if sample.ResultValue > 0:
						sampleList.append(float(sample.ResultValue))
					else:
						sampleList.append(0.1)

				# add to CSV
				#empty list for a row
				row = ['','','','','','','','','','','']
				row[0] = beach.BeachID
				row[1] = sample.BeachName
				row[2] = sample.StationID
				row[3] = sample.StationName
				row[4] = sample.StateCode
				row[5] = sample.CountyName
				row[6] = sample.StartDate
				row[7] = float(sample.ResultValue)
				row[8] = sample.ResultMeasureUnit
				row[9] = sample.CharacteristicName
				row[10] = sample.precipSum

				# write row to CSV
				writer.writerow(row)


	# write to CSV file for all data associated wiht this site

	# select all samples
	allSamples = BeachWQSamples.objects.filter(BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").order_by('StartDate')

	all_csv_path = os.path.join(MEDIA_ROOT + folder + filename_all)
	with open(all_csv_path, 'wb') as f:
		writer = csv.writer(f, quoting=csv.QUOTE_ALL)
		headerRow = ['Beach ID','Beach Name', 'Station ID', 'Station Name', 'State Code', 'County Name', 'Sample Date', 'Result Value', 'Result Measure Unit', 'Characteristic Name', 'Precipitation (In.)']
		writer.writerow(headerRow)

		NumberOfSamples = len(allSamples)
		if NumberOfSamples > 0:
			for sample in allSamples:
				if sample.StartDate < twentySixteen:
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


				sample.precipSum = fortyEightHourPrecip

				# add to CSV
				#empty list for a row
				row = ['','','','','','','','','','','']
				row[0] = beach.BeachID
				row[1] = sample.BeachName
				row[2] = sample.StationID
				row[3] = sample.StationName
				row[4] = sample.StateCode
				row[5] = sample.CountyName
				row[6] = sample.StartDate
				row[7] = float(sample.ResultValue)
				row[8] = sample.ResultMeasureUnit
				row[9] = sample.CharacteristicName
				row[10] = sample.precipSum

				# write row to CSV
				writer.writerow(row)


	# select the most recent sample available
	latestSample = BeachWQSamples.objects.filter(BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").latest('StartDate')
	# earliest sample
	earliestSample = BeachWQSamples.objects.filter(BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").earliest('StartDate')

	# calculate the min, max and mean
	sampleAggregates = BeachWQSamples.objects.filter(StartDate__range=[startDateobject,endDateobject],BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").values('BeachID').annotate(AvgValue=Avg('ResultValue'),MinValue=Min('ResultValue'),MaxValue=Max('ResultValue'))

	#calculate the geometric mean
	geomean = gmean(sampleList)

	print connection.queries

	return render(request, 'explorer/modal.html', {'startDate': startDateobject, 'endDate': endDateobject, 'beach':beach , 'tab':tab ,'scores': scores, 'samples': samples, 'latestSample': latestSample, 'earliestSample': earliestSample, 'sampleAggregates':sampleAggregates, 'geomean':geomean, 'folder':folder, 'filename_all':filename_all, 'filename_filtered':filename_filtered, 'beachStory': story['url']})


def precipApi(request):	
	startDate = request.GET.get("startDate","2000-01-01")
	endDate = request.GET.get("endDate","2100-01-01")
	tab = request.GET.get("tab","timeline")

	# create data objects from start and end dates
	startDateparsed = dateutil.parser.parse(startDate)
	startDateobject = startDateparsed.date()
	endDateparsed = dateutil.parser.parse(endDate)
	endDateobject = endDateparsed.date()

	if startDateobject >= endDateobject:
		endDateobject = startDateobject + relativedelta(years=+1, days=-1)

	#select the monthly scores for this beach in the dates requested
	scores = AnnualScores.objects.filter(Year__range=[startDateobject,endDateobject])

	return render(request, 'explorer/precipVis.html', {'scores':scores, 'startDate':startDateobject, 'endDate':endDateobject, 'tab':tab})


def about(request):
	return render(request, 'explorer/about.html', {})

def datasources(request):
	return render(request, 'explorer/datasources.html', {})

def criteriascoring(request):
	return render(request, 'explorer/criteriascoring.html', {})

def findingssolutions(request):
	return render(request, 'explorer/findingssolutions.html', {})