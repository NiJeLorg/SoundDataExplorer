from django.shortcuts import render
from django.http import JsonResponse

# import all azcase_admin models
from explorer.models import *

#for creating json objects
import json

# for date parsing
import datetime
import dateutil.parser
from dateutil.relativedelta import relativedelta

# Sum
from django.db.models import Sum, Min, Max, Avg, Count

#using scipy to calculae geomean
from scipy.stats import gmean

#for csv tools
import csv

# path to media root for adding a CSV file 
import time
import os
from django.conf import settings
MEDIA_ROOT = settings.MEDIA_ROOT


# Create your views here.
def index(request):	
	tab = "timeline"

	beachId = request.GET.get("beach","")

	endDate = datetime.date(2016, 12, 31)
	startDate = endDate + relativedelta(years=-5, days=+1)

	try:
		beach = Beaches.objects.get(BeachID__exact=beachId)
	except Exception, e:
		beach = None

	#select the monthly scores for this beach in the dates requested
	scores = MonthlyScores.objects.filter(MonthYear__range=[startDate,endDate]).aggregate(NumberOfSamplesSum=Sum('NumberOfSamples'), TotalPassSamplesSum=Sum('TotalPassSamples'), TotalDryWeatherSamplesSum=Sum('TotalDryWeatherSamples'), DryWeatherPassSamplesSum=Sum('DryWeatherPassSamples'), TotalWetWeatherSamplesSum=Sum('TotalWetWeatherSamples'), WetWeatherPassSamplesSum=Sum('WetWeatherPassSamples'))


	return render(request, 'explorer/index.html', {'scores':scores, 'startDate':startDate, 'endDate':endDate, 'tab':tab, 'beachId':beachId, 'beach':beach})

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
		endDateobject = startDateobject + relativedelta(months=1)

	#select all the beaches and loop through them
	beaches = Beaches.objects.all()
	for beach in beaches:
		# for certain BeachID, set end data to last day of sampling regardless of what end data the user chose
		if beach.BeachID == 'CT303091':
			# set end date to last day of year for last season
			endDatefilter = datetime.date(2010, 12, 31)
		else:
			endDatefilter = endDateobject

		#pull data based on date range selected
		scores = MonthlyScores.objects.filter(MonthYear__range=[startDateobject,endDatefilter],BeachID__exact=beach).values('BeachID').annotate(Sum('NumberOfSamples'), Sum('TotalPassSamples'), Sum('TotalDryWeatherSamples'), Sum('DryWeatherPassSamples'), Sum('TotalWetWeatherSamples'), Sum('WetWeatherPassSamples'))

		alltimesamples = MonthlyScores.objects.filter(BeachID__exact=beach).aggregate(Sum('NumberOfSamples'))
		minMaxDate = BeachWQSamples.objects.filter(BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").aggregate(Min('StartDate'), Max('StartDate'))

		# pull beach stories 
		story = {}
		story['url'] = ''
		beachStory = BeachStoryPage.objects.filter(beach__exact=beach).live().public()
		for bs in beachStory:
			story['url'] = bs.url
			


		for score in scores:
			if score['NumberOfSamples__sum'] >= 0:
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
				data['properties']['NumberOfSamples'] = score['NumberOfSamples__sum']
				data['properties']['TotalPassSamples'] = score['TotalPassSamples__sum']
				data['properties']['TotalDryWeatherSamples'] = score['TotalDryWeatherSamples__sum']
				data['properties']['DryWeatherPassSamples'] = score['DryWeatherPassSamples__sum']
				data['properties']['TotalWetWeatherSamples'] = score['TotalWetWeatherSamples__sum']
				data['properties']['WetWeatherPassSamples'] = score['WetWeatherPassSamples__sum']
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

	#setup for CSV files
	ts = str(int(time.time()))
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
		endDateobject = startDateobject + relativedelta(months=+1, days=-1)


	#beach look up
	beach = Beaches.objects.get(BeachID__exact=beachId)

	# pull beach stories 
	story = {}
	story['url'] = ''
	beachStory = BeachStoryPage.objects.filter(beach__exact=beach).live().public()
	for bs in beachStory:
		story['url'] = bs.url	

	#select the monthly scores for this beach in the dates requested
	scores = MonthlyScores.objects.filter(MonthYear__range=[startDateobject,endDateobject],BeachID__exact=beach).values('BeachID').annotate(NumberOfSamplesSum=Sum('NumberOfSamples'), TotalPassSamplesSum=Sum('TotalPassSamples'), TotalDryWeatherSamplesSum=Sum('TotalDryWeatherSamples'), DryWeatherPassSamplesSum=Sum('DryWeatherPassSamples'), TotalWetWeatherSamplesSum=Sum('TotalWetWeatherSamples'), WetWeatherPassSamplesSum=Sum('WetWeatherPassSamples'))

	#list of values to calulate gmean
	sampleList = []

	# select all samples in the range
	samples = BeachWQSamples.objects.filter(StartDate__range=[startDateobject,endDateobject],BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").order_by('StartDate')

	# write to CSV file as we're making the query
	filtered_csv_path = os.path.join(MEDIA_ROOT + folder + filename_filtered)
	with open(filtered_csv_path, 'wb') as f:
		writer = csv.writer(f, quoting=csv.QUOTE_ALL)
		headerRow = ['Beach ID','Beach Name', 'Station ID', 'Station Name', 'State Code', 'County Name', 'Sample Date', 'Result Value', 'Result Measure Unit', 'Characteristic Name', 'Precipitation (In.)', 'Weather Station ID']
		writer.writerow(headerRow)

		NumberOfSamples = len(samples)
		if NumberOfSamples > 0:
			for sample in samples:
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
					# look up Weather Station 
					ws = WeatherStations.objects.get(BeachID__exact=beach)
					stationCode = ws.Icao

				sample.precipSum = precip['PrecipitationIn__sum']

				# make list of sample values for gmean
				# exclude Fecal Coliform from geomean
				if sample.CharacteristicName != "Fecal Coliform":
					if sample.ResultValue > 0:
						sampleList.append(float(sample.ResultValue))
					else:
						sampleList.append(0.1)

				# add to CSV
				#empty list for a row
				row = ['','','','','','','','','','','','']
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
				row[11] = stationCode
				# write row to CSV
				writer.writerow(row)


	# write to CSV file for all data associated wiht this site

	# select all samples
	allSamples = BeachWQSamples.objects.filter(BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").order_by('StartDate')

	all_csv_path = os.path.join(MEDIA_ROOT + folder + filename_all)
	with open(all_csv_path, 'wb') as f:
		writer = csv.writer(f, quoting=csv.QUOTE_ALL)
		headerRow = ['Beach ID','Beach Name', 'Station ID', 'Station Name', 'State Code', 'County Name', 'Sample Date', 'Result Value', 'Result Measure Unit', 'Characteristic Name', 'Precipitation (In.)', 'Weather Station ID']
		writer.writerow(headerRow)

		NumberOfSamples = len(allSamples)
		if NumberOfSamples > 0:
			for sample in allSamples:
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
					# look up Weather Station 
					ws = WeatherStations.objects.get(BeachID__exact=beach)
					stationCode = ws.Icao

				sample.precipSum = precip['PrecipitationIn__sum']

				# make list of sample values for gmean
				# exclude Fecal Coliform from geomean
				if sample.CharacteristicName != "Fecal Coliform":
					if sample.ResultValue > 0:
						sampleList.append(float(sample.ResultValue))
					else:
						sampleList.append(0.1)

				# add to CSV
				#empty list for a row
				row = ['','','','','','','','','','','','']
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
				row[11] = stationCode
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
		endDateobject = startDateobject + relativedelta(months=1)

	#select the monthly scores for this beach in the dates requested
	scores = MonthlyScores.objects.filter(MonthYear__range=[startDateobject,endDateobject]).aggregate(NumberOfSamplesSum=Sum('NumberOfSamples'), TotalPassSamplesSum=Sum('TotalPassSamples'), TotalDryWeatherSamplesSum=Sum('TotalDryWeatherSamples'), DryWeatherPassSamplesSum=Sum('DryWeatherPassSamples'), TotalWetWeatherSamplesSum=Sum('TotalWetWeatherSamples'), WetWeatherPassSamplesSum=Sum('WetWeatherPassSamples'))

	return render(request, 'explorer/precipVis.html', {'scores':scores, 'startDate':startDateobject, 'endDate':endDateobject, 'tab':tab})


def about(request):
	return render(request, 'explorer/about.html', {})

def datasources(request):
	return render(request, 'explorer/datasources.html', {})

def criteriascoring(request):
	return render(request, 'explorer/criteriascoring.html', {})

def findingssolutions(request):
	return render(request, 'explorer/findingssolutions.html', {})