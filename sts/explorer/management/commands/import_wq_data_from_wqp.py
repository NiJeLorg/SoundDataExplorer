import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import csv
import requests
# for date parsing
import datetime
import time
import dateutil.parser


"""
  Loads Water Quality from waterqualitydata.us, replacement for STORET after STORET was decomissioned
"""
class Command(BaseCommand):
    
    def load_BEACON_data(self, params):
        base_url = 'https://www.waterqualitydata.us/data/Result/search?'
        year = '2018'
        
        full_url = base_url + params + '&startDateLo=01-01-'+ year +'&startDateHi=12-31-' + year
        print full_url
        with requests.Session() as s:
            download = s.get(full_url)

            decoded_content = download.content.decode('utf-8')

            cr = csv.reader(decoded_content.splitlines(), delimiter=',')
            my_list = list(cr)
            for row in my_list:
                print(row)
                if row[0] != 'OrganizationIdentifier': # Ignore the header row, import everything else
                    # parse dates
                    # SDparsed = dateutil.parser.parse(row[7])
                    # SDObject = SDparsed.date()
                    # get Beaches object to pass
                    beach_id = row[20].split(';')[1]
                    print beach_id
                    # beach = Beaches.objects.get(BeachID=row[1])

                    # sample = BeachWQSamples()
                    # sample.StateCode = row[0]
                    # sample.BeachID = beach
                    # sample.BeachName = row[2]
                    # sample.StationID = row[3]
                    # sample.StationName = row[4]
                    # sample.CountyName = row[5]
                    # sample.Identifier = row[6]
                    # sample.StartDate = SDObject
                    # sample.StartTime = row[8]
                    # sample.ZoneCode = row[9]
                    # sample.ActivityTypeCode = row[10]
                    # sample.CharacteristicName = row[11]
                    # sample.ResultValue = row[12]
                    # sample.ResultMeasureUnit = row[13]
                    # sample.ResultComment = row[14]
                    # sample.ActivityDepthValue = row[15]
                    # sample.ActivityDepthUnitCode = row[16]
                    # sample.SampleCollectionMethodIdentifier = row[17]
                    # sample.SampleCollectionMethodName = row[18]
                    # sample.FieldGear = row[19]
                    # sample.AnalysisDateTime = row[20]
                    # sample.DetectionQuantitationLimit = row[21]
                    # sample.save()


    def handle(self, *args, **options):
        print "Loading BEACON Data...."
        self.load_BEACON_data('countrycode=US&statecode=US%3A36&countycode=US%3A36%3A119&siteType=Ocean&sampleMedia=Water&characteristicType=Microbiological&providers=STORET&mimeType=csv&zip=no&dataProfile=biological')
        print "Done."




