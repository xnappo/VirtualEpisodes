import requests
import json
import sys
import yaml
import os.path
from utils import getNetwork
from os import path
from shutil import copyfile
import datetime
from datetime import date

with open("config.yaml") as config:
    configData = yaml.load(config, Loader=yaml.FullLoader)

url = "http://" + configData['host'] + \
    "/api/v3/series/?apikey=" + configData['apiKey']
try:
    sys.argv[1]
except:
    print ('Usage: addVirtual.py <partial title of show to add>')
    sys.exit()

jsonResponse = requests.get(url).json()
found = False
for item in jsonResponse:
    if sys.argv[1].lower() in item['title'].lower():
        found = True
        network = getNetwork(item, configData)
        print(network)
        if network in configData['networks']:
            if not path.exists(configData['basePath'] + "/" + item['title']):
                os.mkdir(configData['basePath'] + "/" + item['title'])
            for season in range(1, item['statistics']['seasonCount']+1):
                showSeason = "{:02d}".format(season)
                if not path.exists(configData['basePath'] + "/" + item['title'] + "/Season " + showSeason):
                    os.mkdir(configData['basePath'] + "/" +
                             item['title'] + "/Season " + showSeason)
                url = "http://" + configData['host'] + "/api/v3/episode/?seriesId=" + str(item['id']) + "&seasonNumber=" + str(season) + "&apikey=" + configData['apiKey']
                jsonResponse = requests.get(url).json()
                for episode in jsonResponse:
                    showEpisode = "{:02d}".format(episode['episodeNumber'])
                    airDate = datetime.datetime.strptime(episode['airDate'], "%Y-%m-%d")
                    today = datetime.datetime.strptime(str(date.today()), "%Y-%m-%d")
                    if airDate < today:
                        print ("Adding: " + item['title'] + " " + "S" +
                               showSeason + "E" + showEpisode + " from " + network)
                        if not path.exists(configData['basePath'] + "/" + item['title'] + "/Season " + showSeason + "/" + network + "_S" + showSeason + "E" + showEpisode + ".mp4"):
                            copyfile(configData['dummyFile'], configData['basePath'] + "/" + item['title'] +
                            "/Season " + showSeason + "/" + network + "_S" + showSeason + "E" + showEpisode + ".mp4")
                    else:
                        print ("Not Aired: " + item['title'] + " " + "S" +
                               showSeason + "E" + showEpisode + " from " + network)

if found == False:
    print ('Series: ' +
           sys.argv[1] + ' not found!  Please use addVirtual.py with one of the following series:\n')
    for item in jsonResponse:
        try:
            network = getNetwork(item, configData)
        except:
            network = "unknown"
        if network in configData['networks']:
            print (item['title'] + " [" + network + "]")
