import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import csv
import datetime
from datetime import datetime
from dateutil.rrule import rrule, YEARLY
from dateutil.relativedelta import relativedelta
from django.db.models import Sum



"""
  Export total number of samples pass/fail by beach annually since beginning of dataset
"""
class Command(BaseCommand):
	
	def export_beaches_pass_fail_per_year(self):
		__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
		with open(os.path.join(__location__, 'pass_fail_by_site_per_year.csv'), 'wb') as f:
			writer = csv.writer(f, quoting=csv.QUOTE_ALL)
			#header row
			headerRow = ['Year', 'SiteID', 'Site Name', 'State', 'County', 'Total Number of Passing Samples', 'Number of Samples', 'Percent Pass All Samples', 'Grade All Samples', 'Dry Weather Passing Samples', 'Total Dry Weather Samples', 'Percent Pass Dry Samples', 'Grade Dry Samples', 'Wet Weather Passing Samples', 'Total Wet Weather Samples', 'Percent Pass Wet Samples', 'Grade Wet Samples']
			writer.writerow(headerRow)
			beaches = Beaches.objects.all()
			for beach in beaches:
				latest = datetime(2014, 12, 31)
				earliest = datetime(2003, 1, 1)
				for dateEval in rrule(YEARLY, dtstart=earliest, until=latest):
					firstOfYear = dateEval
					lastOfYear = dateEval + relativedelta(years=+1, days=-1)
					scores = MonthlyScores.objects.filter(MonthYear__range=[firstOfYear,lastOfYear],BeachID__exact=beach).values('BeachID').annotate(Sum('NumberOfSamples'), Sum('TotalPassSamples'), Sum('TotalDryWeatherSamples'), Sum('DryWeatherPassSamples'), Sum('TotalWetWeatherSamples'), Sum('WetWeatherPassSamples'))
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

						row = ['','','','','','','','','','','','','','','','','']
						row[0] = dateEval.strftime('%Y')
						row[1] = beach.BeachID
						row[2] = beach.BeachName
						row[3] = beach.State
						row[4] = beach.County
						row[5] = score['TotalPassSamples__sum']
						row[6] = score['NumberOfSamples__sum']
						row[7] = pctPass
						row[8] = gradeAll
						row[9] = score['DryWeatherPassSamples__sum']
						row[10] = score['TotalDryWeatherSamples__sum']
						row[11] = pctPassDry
						row[12] = gradeDry
						row[13] = score['WetWeatherPassSamples__sum']
						row[14] = score['TotalWetWeatherSamples__sum']
						row[15] = pctPassWet
						row[16] = gradeWet
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
		print "Export Pass/Fail count per beach per year...."
		self.export_beaches_pass_fail_per_year()




