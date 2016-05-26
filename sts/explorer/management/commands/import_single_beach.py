import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import csv


"""
  Loads BEACON beaches from CSV
"""
class Command(BaseCommand):
    
    def load_BEACON_data(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        # open LIS_Beaches_From_Beacon.csv and dump into Beaches table
        with open(os.path.join(__location__, 'SIngle_Beach.csv'), 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                if row[0] != 'State': # Ignore the header row, import everything else
                    beach = Beaches()
                    beach.State = row[0]
                    beach.County = row[1]
                    beach.BeachID = row[2]
                    beach.BeachName = row[3]
                    beach.OwnAccess = row[4]
                    beach.BeachLength = float(row[5])
                    beach.BeachTier = int(row[6])
                    beach.StartLatitude = float(row[7])
                    beach.StartLongitude = float(row[8])
                    beach.EndLatitude = float(row[9])
                    beach.EndLongitude = float(row[10])
                    beach.save()


    def handle(self, *args, **options):
        print "Loading BEACON Data...."
        self.load_BEACON_data()




