# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
import xbmc, xbmcgui, sys, os, re, xbmcvfs, xbmcaddon, random

LOG_ENABLED = False
def log(msg):
    if LOG_ENABLED:
        print "DvdExtras : " + msg

class MusicSettings():
    addon = xbmcaddon.Addon()
    
    def getState(self):
        state = self.addon.getSetting( "themeMusicState" )
        #log( "Current music state " + state )
        return state
        
    def setState(self, state):
        log( "set theme music state " + state )
        self.addon.setSetting( "themeMusicState", state )
        
    def useRandomStart(self):
        return self.addon.getSetting( "themeRandomStart" ) == "true"

    def isEnabled(self):
        return self.addon.getSetting( "themeMusicEnabled" ) == "true"
    
    def isPlaying(self):
        return self.getState() == "PLAYING"
    
    def setPlaying(self):
        self.setState( "PLAYING" )
    
    def isFadingIn(self):
        return self.getState() == "FADE_IN"
        
    def setFadeIn(self):
        self.setState( "FADE_IN" )

    def isFadingOut(self):
        return self.getState() == "FADE_OUT"
    
    def setFadeOut(self):
        self.setState( "FADE_OUT" )
        
    def isStopped(self):
        return self.getState() == "FADE_STOPPED"
        
    def setStopped(self):
        self.setState( "STOPPED" )
        
    def getRestoreVolume( self ):
        return int( self.addon.getSetting( "restoreVolume" ) )
        
    def setRestoreVolume( self, volume ):
        log( "set restore volume %d" % volume )
        self.addon.setSetting( "restoreVolume", str( volume ) )

music = MusicSettings()

class Player():
    def getVolume( self ):
        volume_query = '{"jsonrpc": "2.0", "method": "Application.GetProperties", "params": { "properties": [ "volume" ] }, "id": 1}'
        result = xbmc.executeJSONRPC( volume_query )
        match = re.search( '"volume": ?([0-9]{1,3})', result )
        volume = int( match.group(1) )
        return volume
        
    def setVolume( self, volumeLevel ):
        if volumeLevel < 1:
            volumeLevel = 1
        xbmc.executebuiltin( "XBMC.SetVolume(%d)" % ( volumeLevel ) )
        
    def fade( self, goal, steps, validSetting ):
        current = self.getVolume()
        step = ( current - goal ) / float(steps)
        log( "fade from " + str(current) + " to " + str(goal) + " using steps " + str(step) )
        success = True
        for index in range ( 0, steps - 1 ):
            current -= step
            if music.getState() != validSetting:
                log( "Cancelling fade " + validSetting )
                success = False
                break
            self.setVolume( current )
            xbmc.sleep(50)
        if success:
            self.setVolume( goal )
        return success

    def stop( self ):
        log( "Stopping xbmc player" )
        music.setStopped()
        xbmc.Player().stop()
        
    def fadeOut( self ):
        if music.isPlaying():
            music.setRestoreVolume( self.getVolume() )
        music.setFadeOut()
        if self.fade( 1, 10, "FADE_OUT" ):
            self.stop()
            # wait till player is stopped before raising the volume
            while xbmc.Player().isPlaying():
                xbmc.sleep(50)
            self.setVolume( music.getRestoreVolume() )

    def createPlaylist(self, files ):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        playlist.clear()
        for file in files:
            playlist.add( file )
        return playlist
        
    def fadeIn( self, files, start ):
        goal = self.getVolume()
        if not music.isStopped():
            goal = music.getRestoreVolume()
        self.stop()
        music.setFadeIn()
        self.setVolume( 1 )
        playlist = self.createPlaylist( files )
        xbmc.sleep(200)
        xbmc.Player().play( playlist )
        while not xbmc.Player().isPlayingAudio():
            log( "waiting to play" )
            xbmc.sleep(1)
        xbmc.sleep(300)
        if start == -1:
            random.seed()
            start = random.randint( 0, int(xbmc.Player().getTotalTime() * .75) )        
        xbmc.executebuiltin("xbmc.playercontrol(RepeatAll)")
        xbmc.Player().seekTime( start )
        xbmc.sleep(10)
        if self.fade( goal, 30, "FADE_IN" ):
            music.setPlaying()
    
class Searcher:
    def getMatchingFiles(self, directory, pattern, recursive):
        matches = []
        log( "Searching " + directory + " for " + pattern )
        dirs, files = xbmcvfs.listdir( directory )
        for file in files:
            m = re.search(pattern, file)
            if m:
                path = os.path.join( directory, file )
                log( "Found match: " + path )
                matches.append( path )
        if recursive:
            for dir in dirs:
                matches.extend( self.getMatchingFiles( os.path.join( directory, dir ), pattern, recursive ) )
        return matches

class DvdExtras(xbmcgui.Window):
    def get_movie_sources(self):    
        log( "getting sources" )
        jsonResult = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Files.GetSources", "params": {"media": "video"}, "id": 1}')
        log( jsonResult )
        shares = eval(jsonResult)
        shares = shares['result']['sources']
        
        results = []
        for s in shares:
            share = {}
            share['path'] = s['file']
            share['name'] = s['label']
            log( "found source, path: " + share['path'] + " name: " + share['name'] )
            results.append(share['path'])
            
        return results

    def showList(self, list):
        addPlayAll = len(list) > 1
        if addPlayAll:
            list.insert(0, ("PlayAll", "Play All", "Play All") )
        select = xbmcgui.Dialog().select('Extras', [name[2].replace(".sample","").replace("&#58;", ":") for name in list])
        if select != -1:
            xbmc.executebuiltin("Dialog.Close(all, true)") 
            music.setStopped()
            xbmc.Player().stop()
            if select == 0 and addPlayAll == True:
                playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
                playlist.clear()
                for item in list:
                    log( "Start playing " + item[0] )
                    playlist.add( item[0] )
                xbmc.Player().play( playlist )
            else:
                log( "Start playing " + list[select][0] )
                xbmc.Player().play( list[select][0] )
        
    def showError(self):
        xbmcgui.Dialog().ok("Info", "No extras found")

    def getOrderAndDisplay(self, displayName):
        result = ( displayName, displayName )
        match = re.search("^\[(?P<order>.+)\](?P<Display>.*)", displayName)
        if match:
            orderKey = match.group('order')
            if orderKey != "":
                result = ( orderKey, match.group('Display') )
        return result
        
    def getExtrasDirFiles(self, filepath):
        basepath = os.path.dirname( filepath )
        extrasDir = basepath + "/Extras/"
        log( "Checking existence for " + extrasDir )
        extras = []
        if xbmcvfs.exists( extrasDir ):
            dirs, files = xbmcvfs.listdir( extrasDir )
            for filename in files:
                log( "found file: " )
                log( filename[0] )
                orderDisplay = self.getOrderAndDisplay( os.path.splitext(filename)[0] )
                extras.append( ( extrasDir + filename, orderDisplay[0], orderDisplay[1] ) )
        return extras
        
    def getExtrasFiles(self, filepath):
        extras = []
        directory = os.path.dirname(filepath)
        dirs, files = xbmcvfs.listdir(directory)
        fileWoExt = os.path.splitext( os.path.basename( filepath ) )[0]
        pattern = fileWoExt + "-extras-"
        for file in files:
            m = re.search(pattern + ".*", file)
            if m:
                path = os.path.join( directory, file )
                displayName = os.path.splitext(file[len(pattern):])[0]
                orderDisplay = self.getOrderAndDisplay( displayName )
                extras.append( ( path, orderDisplay[0], orderDisplay[1]  ) )
                log( "Found extras file: " + path + ", " + displayName )
        return extras

    def findExtras(self, path):
        files = self.getExtrasDirFiles(path)
        files.extend( self.getExtrasFiles( path ) )
        files.sort(key=lambda tup: tup[1])
        if not files:
            error = True
        else:
            error = self.showList( files )
        if error:
            self.showError()
    
    def getExtraNfoFiles(self, sources):
        matches = []
        for source in sources:
            matches.extend( Searcher().getMatchingFiles( source, ".*-extras-nfo-.*", True ) )
        log( "Found " + str(len(matches)) + " matches" )
        return matches
        
    def getSeasonAndEpisode(self, filename):
        season = ""
        episode = ""
        m = re.search("[Ss]([0-9]+)[][ ._-]*[Ee]([0-9]+(?:(?:[a-i]|\\.[1-9])(?![0-9]))?)([^\\\\/]*)$", filename)
        if m:
            season = "<season>" + m.group(1) + "</season>"
            episode = "<episode>" + m.group(2) + "</episode>"
        else:
            m = re.search("[\\._ -]()[Ee][Pp]_?([0-9]+(?:(?:[a-i]|\\.[1-9])(?![0-9]))?)([^\\\\/]*)$", filename)
            if m:
                season = "<season>1</season>"
                episode = "<episode>" + m.group(1) + "</episode>"
            else:
                m = re.search("[\\\\/\\._ \\[\\(-]([0-9]+)x([0-9]+(?:(?:[a-i]|\\.[1-9])(?![0-9]))?)([^\\\\/]*)$", filename)
                if m:
                    season = "<season>" + m.group(1) + "</season>"
                    episode = "<episode>" + m.group(2) + "</episode>"
        return ( season, episode )

    def createNfos(self):
        progressDialog = xbmcgui.DialogProgress()
        progressDialog.create( "Extras", "Searching for files" )
        pendingFiles = self.getExtraNfoFiles( self.get_movie_sources() )
        pattern = "-extras-nfo-"
        current = 0
        total = len( pendingFiles )
        for file in pendingFiles:
            current = current + 1
            log( "Creating nfo for " + file )
            progressDialog.update( current / total, "Creating nfo for " + file )
            directory = os.path.dirname( file )
            filename = os.path.basename( file )
            patternStart = filename.index(pattern)
            patternEnd = len( pattern )
            displayName = filename[patternStart + patternEnd:]
            displayName = os.path.splitext(displayName)[0].replace(".sample", "")
            newName = filename[0:patternStart] + "-" + filename[patternStart + patternEnd:]
            newName = newName.replace( ".sample", "" )
            xbmcvfs.rename( file, os.path.join( directory, newName ) )
            seasonAndEpisode = self.getSeasonAndEpisode(filename)
            nfoFile = xbmcvfs.File( os.path.join( directory, os.path.splitext(newName)[0] ) + ".nfo", 'w' )
            nfoFile.write( "<episodedetails><title>" + displayName.replace("&#58;", ":") + "</title>" + seasonAndEpisode[0] + seasonAndEpisode[1] + "</episodedetails>" )
            nfoFile.close()
        progressDialog.close()
        if current > 0:
            xbmc.executebuiltin("UpdateLibrary(video)") 
        xbmcgui.Dialog().ok("Extras", "Finished scan")

class ThemePlayer:
    def getFiles(self, path):
        directory = os.path.dirname(path)
        return Searcher().getMatchingFiles( directory, "theme.*\.mp3", False )

    def getRandomIndex(self, items):
        index = -1
        count = len(items)
        if count >= 1:
            index = 0
            if count > 1:
                random.seed()
                index = random.randint(0, count-1)
        return index
                
    def getSeekStart(self, path):
        startAt = 0
        match = re.search("(?<=\[).+(?=\])", os.path.basename( path ) )
        if match:
            times = match.group( 0 ).split( ",")
            selectedTime = times[self.getRandomIndex( times )]
            if selectedTime == "random":
                startAt = -1
            elif selectedTime.isdigit():
                startAt = int( selectedTime )
        elif music.useRandomStart():
            startAt = -1
        return startAt

    def start(self, path):
        if music.isEnabled():
            themeFiles = self.getFiles(path)
            themeFileCount = len( themeFiles )
            startSong = self.getRandomIndex( themeFiles )
            if startSong != -1:
                playlist = []
                log( "adding %d songs starting at %d" % (themeFileCount, startSong) )
                for i in range( startSong, themeFileCount ):
                    log( "adding song " + themeFiles[i] )
                    playlist.append( themeFiles[i] )
                for i in range( 0, startSong ):
                    log( "adding song " + themeFiles[i] )
                    playlist.append( themeFiles[i] )
                    
                startAt = self.getSeekStart( themeFiles[startSong] )
                Player().fadeIn( playlist, startAt )

    def stop(self):
        if music.isEnabled() and not music.isStopped():
            Player().fadeOut()
    
extras = DvdExtras()
if len(sys.argv) > 1:
    if sys.argv[1] == "stop_theme":
        ThemePlayer().stop()
    else:
        path = sys.argv[1]
        if len(sys.argv) > 2 and sys.argv[2] == "start_theme":
            ThemePlayer().start(path)
        else:
            log( "finding extras for " + sys.argv[1] )
            extras.findExtras(path)
else:
    log( "creating Nfo files" )
    extras.createNfos()