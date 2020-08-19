import xbmc

class XBMCPlayer( xbmc.Player ):
    def __init__( self, *args ):
        pass

    def onPlayBackStarted( self ):
        # Will be called when xbmc starts playing a file
        xbmc.log( "Testing name for Netflix/Amazon dummy match: " + str(self.getPlayingFile(self)) )
        intent   = ''
        dataType = ''
        dataURI  = ''
        if "Netflix_S" in str(self.getPlayingFile(self)):
            xbmc.sleep(400)
            while(self.isPlaying() == True):
                self.seekTime(10)
	        xbmc.sleep(200)
            app      = 'com.netflix.ninja'
            cmd = 'StartAndroidActivity("%s", "%s", "%s", "%s")' % (app, intent, dataType, dataURI)
            xbmc.executebuiltin(cmd)
        elif "Amazon_S" in str(self.getPlayingFile(self)):
            xbmc.sleep(400)
            while(self.isPlaying() == True):
                self.seekTime(10)
            	xbmc.sleep(200)
            app      = 'com.amazon.amazonvideo.livingroom'
            cmd = 'StartAndroidActivity("%s", "%s", "%s", "%s")' % (app, intent, dataType, dataURI)
            xbmc.executebuiltin(cmd)

player = XBMCPlayer()

while not xbmc.abortRequested:
    xbmc.sleep(1000)
