import requests
import json
import yaml
import os.path
from os import path
from shutil import copyfile
from datetime import date
from datetime import timedelta
from utils import getNetwork

# Modify below for debug
daysBack = 9  # Used for debug to get more episodes (should be 0)
# Used for debug to get more episodes, one is actually for current day.
daysAhead = 0 
startDate = date.today() - timedelta(daysBack)
endDate = date.today() + timedelta(daysAhead)
# End of debug section

with open("config.yaml") as config:
    configData = yaml.load(config, Loader=yaml.FullLoader)

url = "http://" + configData['host'] + "/api/v3/calendar/?apikey=" + configData['apiKey'] + \
    "&unmonitored=true&includeSeries=true&start=" + \
    startDate.strftime("%Y-%m-%d") + "&end=" + endDate.strftime("%Y-%m-%d")

jsonResponse = requests.get(url).json()
for item in jsonResponse:
    network = getNetwork(item['series'], configData)
    if network in configData['networks']:
        showSeason = "{:02d}".format(item['seasonNumber'])
        showEpisode = "{:02d}".format(item['episodeNumber'])
        showTitle = (item['series']['title']).replace(':','-')
        print ("Adding: " + showTitle + " " + "S" +
               showSeason + "E" + showEpisode + " from " + network)
        # Make directories/files as needed
        if not path.exists(configData['basePath'] + "/" + showTitle):
            os.mkdir(configData['basePath'] + "/" + showTitle)
        if not path.exists(configData['basePath'] + "/" + showTitle + "/Season " + showSeason):
            os.mkdir(configData['basePath'] + "/" +
                     showTitle + "/Season " + showSeason)
        if not path.exists(configData['basePath'] + "/" + showTitle + "/Season " + showSeason + "/" + network + "_S" + showSeason + "E" + showEpisode + ".mp4"):
            copyfile(configData['dummyFile'], configData['basePath'] + "/" + showTitle +
                     "/Season " + showSeason + "/" + network + "_S" + showSeason + "E" + showEpisode + ".mp4")
