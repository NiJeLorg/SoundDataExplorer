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
from django.db.models import Sum, Min, Max, Avg

#using scipy to calculae geomean
from scipy.stats import gmean


# Create your views here.
def index(request):	
	tab = "timeline"

	# 5 year rolling window
	endDate = datetime.date(datetime.date.today().year, 1, 1)
	startDate = endDate + relativedelta(years=-5)

	#select the monthly scores for this beach in the dates requested
	scores = MonthlyScores.objects.filter(MonthYear__range=[startDate,endDate]).aggregate(NumberOfSamplesSum=Sum('NumberOfSamples'), TotalPassSamplesSum=Sum('TotalPassSamples'), TotalDryWeatherSamplesSum=Sum('TotalDryWeatherSamples'), DryWeatherPassSamplesSum=Sum('DryWeatherPassSamples'), TotalWetWeatherSamplesSum=Sum('TotalWetWeatherSamples'), WetWeatherPassSamplesSum=Sum('WetWeatherPassSamples'))

	return render(request, 'explorer/index.html', {'scores':scores, 'startDate':startDate, 'endDate':endDate, 'tab':tab})

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
		#pull data based on date range selected
		scores = MonthlyScores.objects.filter(MonthYear__range=[startDateobject,endDateobject],BeachID__exact=beach).values('BeachID').annotate(Sum('NumberOfSamples'), Sum('TotalPassSamples'), Sum('TotalDryWeatherSamples'), Sum('DryWeatherPassSamples'), Sum('TotalWetWeatherSamples'), Sum('WetWeatherPassSamples'))
		alltimesamples = MonthlyScores.objects.filter(BeachID__exact=beach).aggregate(Sum('NumberOfSamples'))
		minMaxDate = BeachWQSamples.objects.filter(BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").aggregate(Min('StartDate'), Max('StartDate'))
		for score in scores:
			if score['NumberOfSamples__sum'] > 0:
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
				data['geometry'] = {}
				data['geometry']['type'] = 'Point'
				data['geometry']['coordinates'] = [beach.StartLongitude, beach.StartLatitude]
				response['features'].append(data)



	return JsonResponse(response)


def modalApi(request):	
	startDate = request.GET.get("startDate","2000-01-01")
	endDate = request.GET.get("endDate","2100-01-01")
	beachId = request.GET.get("beachId","")
	tab = request.GET.get("tab","precip")

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

	#select the monthly scores for this beach in the dates requested
	scores = MonthlyScores.objects.filter(MonthYear__range=[startDateobject,endDateobject],BeachID__exact=beach).values('BeachID').annotate(NumberOfSamplesSum=Sum('NumberOfSamples'), TotalPassSamplesSum=Sum('TotalPassSamples'), TotalDryWeatherSamplesSum=Sum('TotalDryWeatherSamples'), DryWeatherPassSamplesSum=Sum('DryWeatherPassSamples'), TotalWetWeatherSamplesSum=Sum('TotalWetWeatherSamples'), WetWeatherPassSamplesSum=Sum('WetWeatherPassSamples'))

	#list got gmean
	sampleList = []

	# select all samples in the range
	samples = BeachWQSamples.objects.filter(StartDate__range=[startDateobject,endDateobject],BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").order_by('StartDate')
	NumberOfSamples = len(samples)
	if NumberOfSamples > 0:
		for sample in samples:
			today = sample.StartDate
			threeDaysAgo = sample.StartDate + relativedelta(days=-3)
			precip = WeatherData.objects.filter(Station__BeachID__exact=beach, Date__gte=threeDaysAgo, Date__lte=today).aggregate(Sum('PrecipitationIn'))
			sample.precipSum = precip['PrecipitationIn__sum']

			# make list of sample values for gmean
			# exclude Fecal Coliform from geomean
			if sample.CharacteristicName != "Fecal Coliform":
				sampleList.append(float(sample.ResultValue))


	# select the most recent sample available
	latestSample = BeachWQSamples.objects.filter(BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").latest('StartDate')
	# earliest sample
	earliestSample = BeachWQSamples.objects.filter(BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").earliest('StartDate')

	# calculate the min, max and mean
	sampleAggregates = BeachWQSamples.objects.filter(StartDate__range=[startDateobject,endDateobject],BeachID__exact=beach).exclude(CharacteristicName__exact="Total Coliform").values('BeachID').annotate(AvgValue=Avg('ResultValue'),MinValue=Min('ResultValue'),MaxValue=Max('ResultValue'))

	#calculate the geometric mean
	geomean = gmean(sampleList)

	return render(request, 'explorer/modal.html', {'startDate': startDateobject, 'endDate': endDateobject, 'beach':beach , 'tab':tab ,'scores': scores, 'samples': samples, 'latestSample': latestSample, 'earliestSample': earliestSample, 'sampleAggregates':sampleAggregates, 'geomean':geomean})


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