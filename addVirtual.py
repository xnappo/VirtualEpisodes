import requests
import json
import sys
import yaml
import os
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
def is_web_mode():
    return os.getenv("AUTOVIRTUAL_WEB") == "1"


try:
    sys.argv[1]
except:
    if not is_web_mode():
        print('Usage: addVirtual.py <partial title of show to add>')
    sys.exit()

jsonResponse = requests.get(url).json()
found = False
for item in jsonResponse:
    if sys.argv[1].lower() in item['title'].lower():
        found = True
        network = getNetwork(item, configData)
        print(network)
        if network not in configData['networks']:
            print("UNMAPPED_NETWORK:" + network)
            continue
        if network in configData['networks']:
            showTitle = (item['title']).replace(':','-')
            if not path.exists(configData['basePath'] + "/" + showTitle):
                os.mkdir(configData['basePath'] + "/" + showTitle)
            for season in range(1, item['statistics']['seasonCount']+1):
                showSeason = "{:02d}".format(season)
                if not path.exists(configData['basePath'] + "/" + showTitle + "/Season " + showSeason):
                    os.mkdir(configData['basePath'] + "/" +
                             showTitle + "/Season " + showSeason)
                url = "http://" + configData['host'] + "/api/v3/episode/?seriesId=" + str(item['id']) + "&seasonNumber=" + str(season) + "&apikey=" + configData['apiKey']
                jsonResponse = requests.get(url).json()
                for episode in jsonResponse:
                    showEpisode = "{:02d}".format(episode['episodeNumber'])
                    air_date_raw = episode.get('airDate') or episode.get('airDateUtc')
                    if not air_date_raw:
                        print ("Skipping: " + showTitle + " " + "S" +
                               showSeason + "E" + showEpisode + " from " + network + " (missing air date)")
                        continue
                    try:
                        if "T" in air_date_raw:
                            airDate = datetime.datetime.fromisoformat(air_date_raw.replace("Z", "+00:00")).date()
                        else:
                            airDate = datetime.datetime.strptime(air_date_raw, "%Y-%m-%d").date()
                    except ValueError:
                        print ("Skipping: " + showTitle + " " + "S" +
                               showSeason + "E" + showEpisode + " from " + network + " (invalid air date)")
                        continue
                    today = date.today()
                    if airDate < today:
                        print ("Adding: " + showTitle + " " + "S" +
                               showSeason + "E" + showEpisode + " from " + network)
                        if not path.exists(configData['basePath'] + "/" + showTitle + "/Season " + showSeason + "/" + network + "_S" + showSeason + "E" + showEpisode + ".mp4"):
                            copyfile(configData['dummyFile'], configData['basePath'] + "/" + showTitle +
                            "/Season " + showSeason + "/" + network + "_S" + showSeason + "E" + showEpisode + ".mp4")
                    else:
                        print ("Not Aired: " + showTitle + " " + "S" +
                               showSeason + "E" + showEpisode + " from " + network)

if found == False:
    if is_web_mode():
        print('Series not found. Series available in Sonarr are below:')
    else:
        print('Series: ' +
              sys.argv[1] + ' not found!  Please use addVirtual.py with one of the following series:\n')
    for item in jsonResponse:
        try:
            network = getNetwork(item, configData)
        except:
            network = "unknown"
        if network in configData['networks']:
            print (item['title'] + " [" + network + "]")
