import requests
import json
import sys
import yaml
import os.path
from os import path
from shutil import copyfile

with open("config.yaml") as config:
    configData = yaml.load(config, Loader=yaml.FullLoader)

url = "http://" + configData['host'] + \
    "/api/series/?apikey=" + configData['apiKey']
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
        if item['network'] in configData['networkMaps']:
            network = configData['networkMaps'][item['network']]
        else:
            network = item['network']

        if network in configData['networks']:
            if not path.exists(configData['basePath'] + "/" + item['title']):
                os.mkdir(configData['basePath'] + "/" + item['title'])
            for season in range(1, item['seasonCount']+1):
                showSeason = "{:02d}".format(season)
                if not path.exists(configData['basePath'] + "/" + item['title'] + "/Season " + showSeason):
                    os.mkdir(configData['basePath'] + "/" +
                             item['title'] + "/Season " + showSeason)
                for episode in range(1, item['seasons'][season-1]['statistics']['totalEpisodeCount']+1):
                    showEpisode = "{:02d}".format(episode)
                    print ("Adding: " + item['title'] + " " + "S" +
                           showSeason + "E" + showEpisode + " from " + network)
                    if not path.exists(configData['basePath'] + "/" + item['title'] + "/Season " + showSeason + "/" + network + "_S" + showSeason + "E" + showEpisode + ".mp4"):
                        copyfile(configData['dummyFile'], configData['basePath'] + "/" + item['title'] +
                                 "/Season " + showSeason + "/" + network + "_S" + showSeason + "E" + showEpisode + ".mp4")
if found == False:
    print ('Series: ' +
           sys.argv[1] + ' not found!  Please use addVirtual.py with one of the following series:\n')
    for item in jsonResponse:
        if item['network'] in configData['networkMaps']:
            network = configData['networkMaps'][item['network']]
        else:
            network = item['network']

        if network in configData['networks']:
            print (item['title'] + " [" + network + "]")
