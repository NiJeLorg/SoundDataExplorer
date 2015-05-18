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
from django.db.models import Sum


# Create your views here.
def index(request):	
	startDate = request.GET.get("startDate","2000-01-01")
	endDate = request.GET.get("endDate","2020-01-01")
	context_dict = {'startDate': startDate, 'endDate': endDate}
	return render(request, 'explorer/index.html', context_dict)

def beaconApi(request):
	response = {}
	response['type'] = "FeatureCollection"
	response['features'] = []

	if request.method == 'GET':
		startDate = request.GET.get("startDate","2000-01-01")
		endDate = request.GET.get("endDate","2020-01-01")
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
					data['properties']['StartDate'] = startDateobject
					data['properties']['EndDate'] = endDateobject
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




