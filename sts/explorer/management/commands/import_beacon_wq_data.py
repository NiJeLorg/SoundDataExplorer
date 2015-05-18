import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import csv
# for date parsing
import datetime
import time
import dateutil.parser


"""
  Loads BEACON Water Quality from CSV
"""
class Command(BaseCommand):
    
    def load_BEACON_data(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        # open LIS_Beacon_Beach_WQdata.csv and dump into BeachWQSamples table
        with open(os.path.join(__location__, 'LIS_Beacon_Beach_WQdata.csv'), 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] != 'StateCode': # Ignore the header row, import everything else
                    # parse dates
                    SDparsed = dateutil.parser.parse(row[7])
                    STparsed = dateutil.parser.parse(row[8])
                    SDObject = SDparsed.date()
                    STObject = STparsed.time()

                    # get Beaches object to pass
                    beach = Beaches.objects.get(BeachID=row[1])

                    sample = BeachWQSamples()
                    sample.StateCode = row[0]
                    sample.BeachID = beach
                    sample.BeachName = row[2]
                    sample.StationID = row[3]
                    sample.StationName = row[4]
                    sample.CountyName = row[5]
                    sample.Identifier = row[6]
                    sample.StartDate = SDObject
                    sample.StartTime = row[8]
                    sample.ZoneCode = row[9]
                    sample.ActivityTypeCode = row[10]
                    sample.CharacteristicName = row[11]
                    sample.ResultValue = row[12]
                    sample.ResultMeasureUnit = row[13]
                    sample.ResultComment = row[14]
                    sample.ActivityDepthValue = row[15]
                    sample.ActivityDepthUnitCode = row[16]
                    sample.SampleCollectionMethodIdentifier = row[17]
                    sample.SampleCollectionMethodName = row[18]
                    sample.FieldGear = row[19]
                    sample.AnalysisDateTime = row[20]
                    sample.DetectionQuantitationLimit = row[21]
                    sample.save()


    def handle(self, *args, **options):
        print "Loading BEACON Data...."
        self.load_BEACON_data()




