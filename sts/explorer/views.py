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


# Create your views here.
def index(request):	
	#startDate = request.GET.get("startDate","2000-01-01")
	#endDate = request.GET.get("endDate","2100-01-01")
	#context_dict = {'startDate': startDate, 'endDate': endDate}
	context_dict = {}
	return render(request, 'explorer/index.html', context_dict)

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

	#select all the beaches and loop through them
	beaches = Beaches.objects.all()
	for beach in beaches:
		#pull data based on date range selected
		scores = MonthlyScores.objects.filter(MonthYear__range=[startDateobject,endDateobject],BeachID__exact=beach).values('BeachID').annotate(Sum('NumberOfSamples'), Sum('TotalPassSamples'), Sum('TotalDryWeatherSamples'), Sum('DryWeatherPassSamples'), Sum('TotalWetWeatherSamples'), Sum('WetWeatherPassSamples'))
		minMaxDate = BeachWQSamples.objects.filter(BeachID__exact=beach).aggregate(Min('StartDate'), Max('StartDate'))
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

	# create data objects from start and end dates
	startDateparsed = dateutil.parser.parse(startDate)
	startDateobject = startDateparsed.date()
	endDateparsed = dateutil.parser.parse(endDate)
	endDateobject = endDateparsed.date()

	#beach look up
	beach = Beaches.objects.get(BeachID__exact=beachId)

	#select the monthly scores for this beach in the dates requested
	scores = MonthlyScores.objects.filter(MonthYear__range=[startDateobject,endDateobject],BeachID__exact=beach).values('BeachID').annotate(NumberOfSamplesSum=Sum('NumberOfSamples'), TotalPassSamplesSum=Sum('TotalPassSamples'), TotalDryWeatherSamplesSum=Sum('TotalDryWeatherSamples'), DryWeatherPassSamplesSum=Sum('DryWeatherPassSamples'), TotalWetWeatherSamplesSum=Sum('TotalWetWeatherSamples'), WetWeatherPassSamplesSum=Sum('WetWeatherPassSamples'))

	# select all samples in the range
	samples = BeachWQSamples.objects.filter(StartDate__range=[startDateobject,endDateobject],BeachID__exact=beach)
	NumberOfSamples = len(samples)
	if NumberOfSamples > 0:
		for sample in samples:
			#skip Total Coliform samples
			if sample.CharacteristicName != 'Total Coliform':
				today = sample.StartDate
				threeDaysAgo = sample.StartDate + relativedelta(days=-3)
				precip = WeatherData.objects.filter(Station__BeachID__exact=beach, Date__gte=threeDaysAgo, Date__lte=today).aggregate(Sum('PrecipitationIn'))
				sample.precipSum = precip['PrecipitationIn__sum']


	# select the most recent sample available
	latestSample = BeachWQSamples.objects.filter(StartDate__range=[startDateobject,endDateobject],BeachID__exact=beach).latest('StartDate')

	# calculate the min, max and geo mean
	sampleAggregates = BeachWQSamples.objects.filter(StartDate__range=[startDateobject,endDateobject],BeachID__exact=beach).values('BeachID').annotate(AvgValue=Avg('ResultValue'),MinValue=Min('ResultValue'),MaxValue=Max('ResultValue'))



	context_dict = {'startDate': startDate, 'endDate': endDate, 'beach':beach ,'scores': scores, 'samples': samples, 'latestSample': latestSample, 'sampleAggregates':sampleAggregates}

	return render(request, 'explorer/modal.html', context_dict)

