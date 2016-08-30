import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import csv
import datetime
from datetime import datetime
from dateutil.rrule import rrule, YEARLY
from dateutil.relativedelta import relativedelta
from django.db.models import Sum

# import settings to point to the media directory
from django.conf import settings


"""
  Export Current 5 year average and Annual grade for most recent 10 years
"""
class Command(BaseCommand):
	
	def export_grades_to_admin_area(self):
		__location__ = settings.MEDIA_ROOT
		with open(os.path.join(__location__, 'documents/beach_grades_5_yr_avg_10_yr_annual.csv'), 'wb') as f:
			writer = csv.writer(f, quoting=csv.QUOTE_ALL)
			# 5 year rolling window
			thisYear = datetime.today().year
			lastYear = thisYear - 1
			endDate = datetime(lastYear, 12, 31)
			fiveYearsAgoDate = endDate + relativedelta(years=-5) + relativedelta(days=1)
			fiveYearsAgoYear = fiveYearsAgoDate.year
			tenYearsAgoDate = endDate + relativedelta(years=-10) + relativedelta(days=1)
			tenYearsAgoYear = tenYearsAgoDate.year

			#header rows
			headerRow1 = ['SiteID', 'Site Name', 'State', 'County', 'Total Number of Passing Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Number of Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Percent Pass All Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Grade All Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Dry Weather Passing Samples  (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Total Dry Weather Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Percent Pass Dry Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Grade Dry Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Wet Weather Passing Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Total Wet Weather Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Percent Pass Wet Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Grade Wet Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')']

			for dateEval in rrule(YEARLY, dtstart=tenYearsAgoDate, until=endDate):
				year = str(dateEval.year)
				addToHeader = ['Percent Pass All Samples (' + year + ')', 'Grade All Samples (' + year + ')']
				headerRow1.extend(addToHeader)

			writer.writerow(headerRow1)


			beaches = Beaches.objects.all()
			for beach in beaches:
				scores = MonthlyScores.objects.filter(MonthYear__range=[fiveYearsAgoDate,endDate],BeachID__exact=beach).values('BeachID').annotate(Sum('NumberOfSamples'), Sum('TotalPassSamples'), Sum('TotalDryWeatherSamples'), Sum('DryWeatherPassSamples'), Sum('TotalWetWeatherSamples'), Sum('WetWeatherPassSamples'))
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

					row = []
					row.append(beach.BeachID) 
					row.append(beach.BeachName)
					row.append(beach.State)
					row.append(beach.County)
					row.append(score['TotalPassSamples__sum'])
					row.append(score['NumberOfSamples__sum'])
					row.append(pctPass)
					row.append(gradeAll)
					row.append(score['DryWeatherPassSamples__sum'])
					row.append(score['TotalDryWeatherSamples__sum'])
					row.append(pctPassDry)
					row.append(gradeDry)
					row.append(score['WetWeatherPassSamples__sum'])
					row.append(score['TotalWetWeatherSamples__sum'])
					row.append(pctPassWet)
					row.append(gradeWet)

					for dateEval in rrule(YEARLY, dtstart=tenYearsAgoDate, until=endDate):
						firstOfYear = dateEval
						lastOfYear = dateEval + relativedelta(years=+1, days=-1)
						scores = MonthlyScores.objects.filter(MonthYear__range=[firstOfYear,lastOfYear],BeachID__exact=beach).values('BeachID').annotate(Sum('NumberOfSamples'), Sum('TotalPassSamples'))
						for score in scores:

							#calculate pct pass and passing grade in total
							if score['NumberOfSamples__sum'] > 0:
								pctPass = (float(score['TotalPassSamples__sum']) / float(score['NumberOfSamples__sum'])) * 100
								pctPass = round(pctPass, 2)
								gradeAll = self.calcGrade(pctPass)
							else:
								pctPass = ''
								gradeAll = ''

							row.append(pctPass)
							row.append(gradeAll)


					writer.writerow(row)

	def calcGrade(self, pct):
		if pct >= 99:
			return 'A+'
		elif pct >= 97:
			return 'A'
		elif pct >= 95:
			return 'A-'
		elif pct >= 93:
			return 'B+'
		elif pct >= 91:
			return 'B'
		elif pct >= 89:
			return 'B-'
		elif pct >= 87:
			return 'C+'
		elif pct >= 85:
			return 'C'
		elif pct >= 83:
			return 'C-'
		elif pct >= 81:
			return 'D+'
		elif pct >= 79:
			return 'D'
		elif pct >= 77:
			return 'D-'
		elif pct >= 0:
			return 'F'
		else:
			return ''


	def handle(self, *args, **options):
		print "Export current 5 year average and annual grade for most recent 10 years...."
		self.export_grades_to_admin_area()




