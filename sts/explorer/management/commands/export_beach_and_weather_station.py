import sys,os
from django.core.management.base import BaseCommand, CommandError
from explorer.models import *
import csv


"""
  Loads BEACON beaches from CSV
"""
class Command(BaseCommand):
    
    def export_beaches_and_weather_stations(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        # open LIS_Beaches_From_Beacon.csv and dump into Beaches table
        with open(os.path.join(__location__, 'beaches_and_weather_stations.csv'), 'wb') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            #header row
            headerRow = ['State','County','BeachID','Beach Name', 'Weather Station ID']
            writer.writerow(headerRow)
            beaches = Beaches.objects.all()
            for beach in beaches:
                #empty list for a row
                row = ['','','','','']
                # select associated weather staions
                ws = WeatherStations.objects.filter(BeachID=beach)
                for w in ws:
                    row[0] = beach.State
                    row[1] = beach.County
                    row[2] = beach.BeachID
                    row[3] = beach.BeachName
                    if w.PwsId:
                        row[4] = w.PwsId
                    else:
                        row[4] = w.Icao
                    writer.writerow(row)


    def handle(self, *args, **options):
        print "Export beaches and Weather Stations...."
        self.export_beaches_and_weather_stations()




