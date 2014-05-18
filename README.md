**This Add-on is Deprecated**

Please look at http://wiki.xbmc.org/index.php?title=Add-on:VideoExtras instead.

xbmc-dvdextras
==============
DvdExtras is an xbmc script that provides a way to associate DVD bonus features with movies or tv shows.

Installation
--------------
Download the latest release from the downloads and install from zip file in xbmc.

Setup
--------------
### File naming convention
For the script to find your files you must follow a specific naming convention. Here are the supported conventions.

#### Extras Folder
If you put all of your movies in their own folder you can simply add an "Extras" sub folder and add all of
your bonus content in that directory.  The script will simply display the filename (without extension) in the UI. By default the list of videos
will appear in alphabetical order.  If you would like to specify a custom order just start the filename with brackets containing the text to sort on.
For example you could create files "[0]Deleted Scenes.mkv", "[1]Bloopers.mkv", and "[2]Behind The Scenes.mkv".  In this case instead of sorting on the name
it will sort on the numbers.  The bracket portion of the filename will not be displayed in the UI.  

#### Same Directory
If for some reason you don't want to create an Extras folder or you want to associate a bonus feature with a specific tv show episode there is an alternative naming convention.
Simply use the same name as the file you want to associate the extra feature with and then append "-extras-Display name here".  So if you wanted to associate an Extended Pilot feature
with the first episode of a tv show named "s1e1.mkv", you would create a file name "s1e1-extras-Extended Pilot.mkv".  When the script displays this file in the UI it will strip out all the
extra stuff and just show "Extended Pilot". To customize the order here you can use the same format as the extras folder.  Example: "s1e1-extras-[99]Extended Pilot.mkv"

#### Tv Show Season Features
Some Dvd extra features for TV shows don't really go with a specific episode and instead just belong to a season.  In this case what I do is just create fake episodes at the end of the
season for these features and make nfo files for the library to parse.  Since I don't really like making the files by hand I added functionality to the script to do this as well, but it requires 
another special file name.  If the season has 19 real episodes and you want to add a fake 20th episode for behind the scenes you would name the file like this "s1e20-extras-nfo-Behind the Scenes.mkv"
Once you have made all of these types of files go to Programs in xbmc and run the DvdExtras script.  It will search for all files in this format and create nfo files with the season, episode, and
title provided by the filename.  Then it will trigger a library update so that the xbmc scanner will include them in the library.


### XBMC File Exclusions
Since these are video files sprinkled in among all of your other video files we need to tell the xbmc scanner to ignore these files.  If we don't then the scanner will try and match
them up with one of the online sites and you probably won't be happy with the results.  To do this we just need to add some new regular expressions to the [advanced settings](http://wiki.xbmc.org/index.php?title=Advancedsettings.xml).
These are the settings that I added.  It is recommended to add these settings and reboot xbmc for them to take effect before adding the files to your library so the scanner doesn't try to parse them.
```xml
<video>
  <excludefromscan>
    <regexp>-extras-</regexp>
    <regexp>[\\/]Extras[\\/]</regexp>
  </excludefromscan>
  <excludetvshowsfromscan>
    <regexp>-extras-</regexp>
    <regexp>[\\/]Extras[\\/]</regexp>
  </excludetvshowsfromscan>
</video>
```


### Skin Modifications
Finally we need to add an extras button to the skin so that we can actually see the extras in the UI.  This is a fairly simple process but will depend on your selected skin. The
file that needs modified is DialogVideoInfo.xml.  This is the code I added to the skin I use (Aeon Nox).  You should be able to use something similar for other skins.
```xml
<control type="button" id="100">
    <description>Extras</description>
    <include>DialogVideoInfoButton</include>
    <label>Extras</label>
    <onclick>XBMC.RunScript(script.dvdextras,$INFO[ListItem.FilenameAndPath])</onclick>
    <visible>[Container.Content(movies) | Container.Content(episodes)] + System.HasAddon(script.dvdextras)</visible>
</control>
```                                             

### Other
After playing around with the script I decided that I personally liked having extras that appeared at the end of a Season to appear in the format "Bonus: Behind the Scenes". Since
adding a colon in a filename can be a problem the script supports the html code &amp;#58; for colon.  So if you create a file with that code in it it will display as a colon in the UI.

### Theme music
If you would like to play music when viewing movie information just add a theme.mp3 file to your movie folder.  You also must update your skin's DialogVideoInfo.xml file to include these two
commands.  This will only play music for movies so that it does not interfere with the TvTunes addon.
```xml
<onload condition="System.HasAddon(script.dvdextras) + Container.Content(movies)">XBMC.RunScript(script.dvdextras,$INFO[ListItem.FilenameAndPath],start_theme)</onload>
<onunload condition="System.HasAddon(script.dvdextras) + Container.Content(movies)">XBMC.RunScript(script.dvdextras,stop_theme)</onunload>
```
#### Customizing theme music
You can actually add more than one theme song for a movie just make sure they all start with theme.  So something like "theme.mp3", "theme1.mp3", or "themeAntyhingCanGoHere.mp3".
If multiple mp3 files are found the script will randomly pick one to start with and if that song finishes it will go on to the next song.  There is also a configurable option to 
select a random start point.  That way you won't always here the same bit of music each time you view the info screen.  You can also manually set start points for a song in case there
are a few passages in a song you really like.  To do this just specify the number of seconds where the song should start.  If multiple start points are given the scrit will randomly
pick one.

theme[10].mp3 - Song will start playing at the 10 second mark

theme[10,152].mp3 - Song will start playing at either 10 seconds or 152 seconds

theme[10,152,random].mp3 - Song will start playing at either 10 seconds, 152 seconds, or a random location

If this format is used on a file it will override the global random start configuration for this specific file.
