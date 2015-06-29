import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import csv
import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum



"""
  Export total number of samples pass/fail by beach for last 5 years
"""
class Command(BaseCommand):
	
	def export_beaches_pass_fail(self):
		__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
		with open(os.path.join(__location__, 'pass_fail_by_site.csv'), 'wb') as f:
			writer = csv.writer(f, quoting=csv.QUOTE_ALL)
			#header row
			headerRow = ['SiteID', 'Site Name', 'State', 'County', 'Total Number of Passing Samples', 'Number of Samples', 'Percent Pass All Samples', 'Grade All Samples', 'Dry Weather Passing Samples', 'Total Dry Weather Samples', 'Percent Pass Dry Samples', 'Grade Dry Samples', 'Wet Weather Passing Samples', 'Total Wet Weather Samples', 'Percent Pass Wet Samples', 'Grade Wet Samples']
			writer.writerow(headerRow)
			# 5 year rolling window
			endDate = datetime.date.today()
			startDate = endDate + relativedelta(years=-5)

			beaches = Beaches.objects.all()
			for beach in beaches:
				scores = MonthlyScores.objects.filter(MonthYear__range=[startDate,endDate],BeachID__exact=beach).values('BeachID').annotate(Sum('NumberOfSamples'), Sum('TotalPassSamples'), Sum('TotalDryWeatherSamples'), Sum('DryWeatherPassSamples'), Sum('TotalWetWeatherSamples'), Sum('WetWeatherPassSamples'))
				for score in scores:

					#calculate pct pass and passing grade in total
					if score['NumberOfSamples__sum'] > 0:
						pctPass = (float(score['TotalPassSamples__sum']) / float(score['NumberOfSamples__sum'])) * 100
						pctPass = round(pctPass, 2)
						gradeAll = self.calcGrade(pctPass)
					else:
						pctPass = ''
						gradeAll = ''

					#calculate pct pass and passing grade dry weather
					if score['TotalDryWeatherSamples__sum'] > 0:
						pctPassDry = (float(score['DryWeatherPassSamples__sum']) / float(score['TotalDryWeatherSamples__sum'])) * 100
						pctPassDry = round(pctPassDry, 2)
						gradeDry = self.calcGrade(pctPassDry)
					else:
						pctPassDry = ''
						gradeDry = ''

					#calculate pct pass and passing grade wet weather
					if score['TotalWetWeatherSamples__sum']:
						pctPassWet = (float(score['WetWeatherPassSamples__sum']) / float(score['TotalWetWeatherSamples__sum'])) * 100
						pctPassWet = round(pctPassWet, 2)
						gradeWet = self.calcGrade(pctPassWet)
					else:
						pctPassWet = ''
						gradeWet = ''

					row = ['','','','','','','','','','','','','','','','']
					row[0] = beach.BeachID
					row[1] = beach.BeachName
					row[2] = beach.State
					row[3] = beach.County
					row[4] = score['TotalPassSamples__sum']
					row[5] = score['NumberOfSamples__sum']
					row[6] = pctPass
					row[7] = gradeAll
					row[8] = score['DryWeatherPassSamples__sum']
					row[9] = score['TotalDryWeatherSamples__sum']
					row[10] = pctPassDry
					row[11] = gradeDry
					row[12] = score['WetWeatherPassSamples__sum']
					row[13] = score['TotalWetWeatherSamples__sum']
					row[14] = pctPassWet
					row[15] = gradeWet
					writer.writerow(row)

	def calcGrade(self, pct):
		if pct > 95:
			return 'A'
		elif pct > 90:
			return 'B'
		elif pct > 85:
			return 'C'
		elif pct > 78:
			return 'D'
		elif pct >= 0:
			return 'F'
		else:
			return ''


	def handle(self, *args, **options):
		print "Export Pass/Fail count per beach...."
		self.export_beaches_pass_fail()




