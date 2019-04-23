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
                if row[0] != 'OrganizationIdentifier': # Ignore the header row, import everything else
                    # parse dates
                    SDparsed = dateutil.parser.parse(row[6])
                    SDObject = SDparsed.date()
                    # get Beaches object to pass
                    beach_id = row[20].split(';')[1]
                    print beach_id
                    beach = Beaches.objects.get(BeachID=beach_id)

                    sample = BeachWQSamples()
                    sample.BeachID = beach
                    sample.BeachName = beach.BeachName
                    sample.StationID = row[22]
                    sample.Identifier = row[0]
                    sample.StartDate = SDObject
                    sample.StartTime = row[7]
                    sample.ZoneCode = row[8]
                    sample.ActivityTypeCode = row[3]
                    sample.CharacteristicName = row[74]
                    sample.ResultValue = row[76]
                    sample.ResultMeasureUnit = row[77]
                    sample.ResultComment = row[91]
                    sample.ActivityDepthValue = row[13]
                    sample.ActivityDepthUnitCode = row[14]
                    sample.SampleCollectionMethodIdentifier = row[54]
                    sample.SampleCollectionMethodName = row[55]
                    sample.FieldGear = row[59]
                    sample.AnalysisDateTime = row[129]
                    sample.DetectionQuantitationLimit = row[136]
                    sample.save()


    def handle(self, *args, **options):
        print "Loading BEACON Data...."
        # Westchester County
        self.load_BEACON_data('countrycode=US&statecode=US%3A36&countycode=US%3A36%3A119&siteType=Ocean&sampleMedia=Water&characteristicType=Microbiological&providers=STORET&mimeType=csv&zip=no&dataProfile=biological')
        # Bronx County
        self.load_BEACON_data('countrycode=US&statecode=US%3A36&countycode=US%3A36%3A005&siteType=Ocean&sampleMedia=Water&characteristicType=Microbiological&providers=STORET&mimeType=csv&zip=no&dataProfile=biological')
        # CT
        self.load_BEACON_data('siteType=Ocean&organization=1CTDPHBM&sampleMedia=Water&characteristicType=Microbiological&providers=STORET&mimeType=csv&zip=yes&dataProfile=biological')
        # Northern Long Island Watershed -- 02030201
        self.load_BEACON_data('countrycode=US&siteType=Ocean&huc=02030201&sampleMedia=Water&characteristicType=Microbiological&providers=STORET&mimeType=csv&zip=no&dataProfile=biological')
        # Fisher's Island
        self.load_BEACON_data('bBox=-72.00%2C41.235834%2C-71.912088%2C41.298513&siteType=Ocean&sampleMedia=Water&characteristicType=Microbiological&providers=STORET&mimeType=csv&zip=no&dataProfile=biological')        
        print "Done."




