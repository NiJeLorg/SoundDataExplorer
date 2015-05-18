import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import csv
from datetime import datetime
from dateutil.rrule import rrule, YEARLY
from dateutil.relativedelta import relativedelta



"""
  Loads BEACON beaches from CSV
"""
class Command(BaseCommand):
	
	def export_count_of_samples_per_year(self):
		__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
		# open LIS_Beaches_From_Beacon.csv and dump into Beaches table
		with open(os.path.join(__location__, 'samples_per_year.csv'), 'wb') as f:
			writer = csv.writer(f, quoting=csv.QUOTE_ALL)
			#header row
			headerRow = ['State','County','BeachID','Beach Name', 'Year', 'Sample Count']
			writer.writerow(headerRow)
			beaches = Beaches.objects.all()
			for beach in beaches:
				today = datetime.today()
				earliest = datetime(2003, 1, 1)
				for dateEval in rrule(YEARLY, dtstart=earliest, until=today):
					firstOfYear = dateEval
					lastOfYear = dateEval + relativedelta(years=+1, days=-1)
					sampleCount = BeachWQSamples.objects.filter(BeachID__exact=beach, StartDate__gte=firstOfYear, StartDate__lte=lastOfYear).count()
					#empty list for a row
					row = ['','','','','','']
					row[0] = beach.State
					row[1] = beach.County
					row[2] = beach.BeachID
					row[3] = beach.BeachName
					row[4] = dateEval.strftime('%Y')
					row[5] = sampleCount
					writer.writerow(row)


	def handle(self, *args, **options):
		print "Export count of samples per year...."
		self.export_count_of_samples_per_year()




