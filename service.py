import xbmc

class XBMCPlayer( xbmc.Player ):
    def __init__( self, *args ):
        pass

    def onPlayBackStarted( self ):
        # Will be called when xbmc starts playing a file
        # Define services and app names, add the _S just in case you have a show/movie called 'Amazon' or something
        services = {
            'Amazon_S':'com.amazon.amazonvideo.livingroom', 
            'Netflix_S':'com.netflix.ninja', 
            'HBO_S':'com.hbo.hbonow', 
            'Discovery_S':'com.discovery.discoveryplus.androidtv'
        }

        xbmc.log( "Testing name for Netflix/Amazon/HBOMax dummy match: " + str(self.getPlayingFile(self)) )
        # Go through our list of streaming services
        for service in services:
            # Check if the playing file matches a streaming service
            if service in str(self.getPlayingFile(self)):
                # This bit below is to ensure the show gets marked watched
                xbmc.sleep(400)
                while(self.isPlaying() == True):
                    self.seekTime(10)
                xbmc.sleep(200)

                # This command's argument are app, intent, dataType and dataURI, but currently
                # no way to make use of the intent etc to go to a particular show. (please let me know!)
                cmd = 'StartAndroidActivity("%s", "%s", "%s", "%s")' % (services[service], '', '', '')
                
                # Run the command
                xbmc.executebuiltin(cmd)

player = XBMCPlayer()

while not xbmc.abortRequested:
    xbmc.sleep(1000)