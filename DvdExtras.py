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
import xbmc, xbmcgui, sys, os, re, xbmcvfs

LOG_ENABLED = False
def log(msg):
    if LOG_ENABLED:
        print "DvdExtras : " + msg

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
        select = xbmcgui.Dialog().select('DVD Extras', [name[1].replace(".sample","").replace("&#58;", ":") for name in list])
        if select != -1:
            xbmc.Player( xbmc.PLAYER_CORE_MPLAYER ).play( list[select][0] )
        
    def showError(self):
        xbmcgui.Dialog().ok("Info", "No extras found")

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
                extras.append( ( extrasDir + filename, os.path.splitext(filename)[0] ) )
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
                extras.append( ( path, displayName ) )
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

    def getExtraNfoFiles(self, sources):
        matches = []
        for source in sources:
            matches.extend( self.getMatchingFiles( source, ".*-extras-nfo-.*", True ) )
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
        progressDialog.create( "Dvd Extras", "Searching for files" )
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
        xbmcgui.Dialog().ok("Dvd Extras", "Finished scan")
    
extras = DvdExtras()
if len(sys.argv) > 1:
    log( "finding extras for " + sys.argv[1] )
    path = sys.argv[1]
    extras.findExtras(path)
else:
    log( "creating Nfo files" )
    extras.createNfos()