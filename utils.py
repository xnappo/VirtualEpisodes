def getNetwork(item, configData):
    # Check for network maps (eg: map all BBCONE shows to HBOMAX)
    if item['network'] in configData['networkMaps']:
        network = configData['networkMaps'][item['network']]
    else:
        network = item['network']

    # Check for show maps (eg: map Peaky Blinders to Netflix)
    for show in configData['showMaps']:
        if show.lower() in item['title'].lower():
            network = configData['showMaps'][show]
    return network
