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
			headerRow1 = ['SiteID', 'Site Name', 'State', 'County', 'Total Number of Passing Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Number of Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Percent Pass All Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Dry Weather Passing Samples  (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Total Dry Weather Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Percent Pass Dry Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Wet Weather Passing Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Total Wet Weather Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')', 'Percent Pass Wet Samples (' + str(fiveYearsAgoYear) + ' to ' + str(lastYear) + ')']

			for dateEval in rrule(YEARLY, dtstart=tenYearsAgoDate, until=endDate):
				year = str(dateEval.year)
				addToHeader = ['Percent Pass Dry Samples (' + year + ')', 'Percent Pass Wet Samples (' + year + ')', 'Maximum Magnitude Dry (' + year + ')', 'Maximum Magnitude Wet (' + year + ')', 'Total Points (' + year + ')', 'Grade (' + year + ')']
				headerRow1.extend(addToHeader)

			writer.writerow(headerRow1)


			beaches = Beaches.objects.all()
			for beach in beaches:
				scores = AnnualScores.objects.filter(Year__range=[fiveYearsAgoDate,endDate],BeachID__exact=beach).values('BeachID').annotate(Sum('NumberOfSamples'), Sum('TotalPassSamples'), Sum('TotalDryWeatherSamples'), Sum('DryWeatherPassSamples'), Sum('TotalWetWeatherSamples'), Sum('WetWeatherPassSamples'))
				for score in scores:

					#calculate pct pass and passing grade in total
					if score['NumberOfSamples__sum'] > 0:
						pctPass = (float(score['TotalPassSamples__sum']) / float(score['NumberOfSamples__sum'])) * 100
						pctPass = round(pctPass, 2)
					else:
						pctPass = ''

					#calculate pct pass and passing grade dry weather
					if score['TotalDryWeatherSamples__sum'] > 0:
						pctPassDry = (float(score['DryWeatherPassSamples__sum']) / float(score['TotalDryWeatherSamples__sum'])) * 100
						pctPassDry = round(pctPassDry, 2)
					else:
						pctPassDry = ''

					#calculate pct pass and passing grade wet weather
					if score['TotalWetWeatherSamples__sum']:
						pctPassWet = (float(score['WetWeatherPassSamples__sum']) / float(score['TotalWetWeatherSamples__sum'])) * 100
						pctPassWet = round(pctPassWet, 2)
					else:
						pctPassWet = ''

					row = []
					row.append(beach.BeachID) 
					row.append(beach.BeachName)
					row.append(beach.State)
					row.append(beach.County)
					row.append(score['TotalPassSamples__sum'])
					row.append(score['NumberOfSamples__sum'])
					row.append(pctPass)
					row.append(score['DryWeatherPassSamples__sum'])
					row.append(score['TotalDryWeatherSamples__sum'])
					row.append(pctPassDry)
					row.append(score['WetWeatherPassSamples__sum'])
					row.append(score['TotalWetWeatherSamples__sum'])
					row.append(pctPassWet)

				for dateEval in rrule(YEARLY, dtstart=tenYearsAgoDate, until=endDate):
					firstOfYear = dateEval
					lastOfYear = dateEval + relativedelta(years=+1, days=-1)
					scores = AnnualScores.objects.filter(Year__range=[firstOfYear,lastOfYear],BeachID__exact=beach)
					for score in scores:

						#calculate pct pass and passing grade in total
						if score.TotalDryWeatherSamples > 0:
							pctPassDry = (float(score.DryWeatherPassSamples) / float(score.TotalDryWeatherSamples)) * 100
							pctPassDry = round(pctPassDry, 2)
							dryFrequencyPoints = self.FrequencyPoints(100-pctPassDry)
						else:
							pctPassDry = ''
							dryFrequencyPoints = 0

						if score.TotalWetWeatherSamples > 0:
							pctPassWet = (float(score.WetWeatherPassSamples) / float(score.TotalWetWeatherSamples)) * 100
							pctPassWet = round(pctPassWet, 2)
							wetFrequencyPoints = self.FrequencyPoints(100-pctPassWet)
						else:
							pctPassWet = ''	
							wetFrequencyPoints = 0	

						if dryFrequencyPoints == 0:
							dryFrequencyPoints = wetFrequencyPoints

						if wetFrequencyPoints == 0:
							wetFrequencyPoints = dryFrequencyPoints
						
						dryMagnitudePoints = self.MagnitudePoints(score.MaxValueDry)
						wetMagnitudePoints = self.MagnitudePoints(score.MaxValueWet)

						totalPoints = dryFrequencyPoints + wetFrequencyPoints + dryMagnitudePoints + wetMagnitudePoints

						grade = self.calcGrade(totalPoints)
						

						row.append(pctPassDry)
						row.append(pctPassWet)
						row.append(score.MaxValueDry)
						row.append(score.MaxValueWet)
						row.append(totalPoints)
						row.append(grade)



				writer.writerow(row)


	def MagnitudePoints(self, d):
		if d > 1040:
			return 1
		elif d > 521:
			return 3
		elif d > 105:
			return 5
		else:
			return 7

	def FrequencyPoints(self, d):
		if d > 23:
			return 1
		elif d > 10:
			return 3
		elif d > 5:
			return 5
		else:
			return 7
	

	def calcGrade(self, points):
		if points >= 27:
			return 'A+'
		elif points >= 25:
			return 'A'
		elif points >= 23:
			return 'A-'
		elif points >= 21:
			return 'B+'
		elif points >= 19:
			return 'B'
		elif points >= 17:
			return 'B-'
		elif points >= 15:
			return 'C+'
		elif points >= 13:
			return 'C'
		elif points >= 11:
			return 'C-'
		elif points >= 9:
			return 'D+'
		elif points >= 7:
			return 'D'
		elif points >= 5:
			return 'D-'
		elif points >= 0:
			return 'F'
		else:
			return ''

	def handle(self, *args, **options):
		print "Export current 5 year average and annual grade for most recent 10 years...."
		self.export_grades_to_admin_area()




