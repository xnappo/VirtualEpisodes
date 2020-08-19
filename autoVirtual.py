import requests
import json
import yaml
import os.path
from os import path
from shutil import copyfile
from datetime import date
from datetime import timedelta

# Modify below for debug
daysBack = 0 # Used for debug to get more episodes
daysAhead = 1 # Used for debug to get more episodes, one is actually for current day.
startDate = date.today() - timedelta(daysBack) 
endDate = date.today() + timedelta(daysAhead)
# End of debug section

with open("config.yaml") as config:
    configData = yaml.load(config)

url = "http://" + configData['host'] + "/api/calendar/?apikey=" + configData['apiKey'] + "&unmonitored=true&start=" + startDate.strftime("%Y-%m-%d") + "&end=" + endDate.strftime("%Y-%m-%d")

jsonResponse = requests.get(url).json()
for item in jsonResponse:
    if "Netflix" in item['series']['network'] or "Amazon" in item['series']['network']:
        showSeason = "{:02d}".format(item['seasonNumber'])
        showEpisode = "{:02d}".format(item['episodeNumber'])
        print ("Adding: " + item['series']['title'] + " " + "S" + showSeason + "E" + showEpisode + " from " + item['series']['network'])
        # Make directories/files as needed
        if not path.exists(configData['basePath'] + "/" + item['series']['title']):
            os.mkdir(basePath + "/" + item['series']['title'])
        if not path.exists(configData['basePath'] + "/" + item['series']['title'] + "/Season " + showSeason):
            os.mkdir(basePath + "/" + item['series']['title'] + "/Season " + showSeason)
        if not path.exists(configData['basePath'] + "/" + item['series']['title'] + "/Season " + showSeason + "/" + item['series']['network'] + "_S" + showSeason + "E" + showEpisode + ".mp4"):
            copyfile(configData['dummyFile'], configData['basePath'] + "/" + item['series']['title'] + "/Season " + showSeason + "/" + item['series']['network'] + "_S" + showSeason + "E" + showEpisode + ".mp4")
