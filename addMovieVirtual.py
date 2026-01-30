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

with open("config_movies.yaml") as config:
    configData = yaml.load(config, Loader=yaml.FullLoader)

try:
    sys.argv[1]
    sys.argv[2]
except:
    print ('Usage: addMovieVirtual.py <"Title", "Service">')
    sys.exit()

network = sys.argv[2]
print(network)
if network in configData['networks']:
    if not path.exists(configData['basePath'] + "/" + sys.argv[1]):
        os.mkdir(configData['basePath'] + "/" + sys.argv[1])
    print ("Adding: " + sys.argv[1] + " from " + network)
    if not path.exists(configData['basePath'] + "/" + sys.argv[1] + "/" + network + "_STREAM" + ".mp4"):
        copyfile(configData['dummyFile'], configData['basePath'] + "/" + sys.argv[1] + "/" + network + "_STREAM" + ".mp4")
