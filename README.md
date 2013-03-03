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
your bonus content in that directory.  The script will simply display the filename (without extension) in the UI. 

#### Same Directory
If for some reason you don't want to create an Extras folder or you want to associate a bonus feature with a specific tv show episode there is an alternative naming convention.
Simply use the same name as the file you want to associate the extra feature with and then append "-extras-Display name here".  So if you wanted to associate an Extended Pilot feature
with the first episode of a tv show named "s1e1.mkv", you would create a file name "s1e1-extras-Extended Pilot.mkv".  When the script displays this file in the UI it will strip out all the
extra stuff and just show "Extended Pilot".

#### Tv Show Season Features
Some Dvd extra features for TV shows don't really go with a specific episode and instead just belong to a season.  In this case what I do is just create fake episodes at the end of the
season for these features and make nfo files for the library to parse.  Since I don't really like making the files by hand I added functionality to the script to do this as well, but it requires 
another special file name.  If the season has 19 real episodes and you want to add a fake 20th episode for behind the scenes you would name the file like this "s1e20-extras-nfo-Behind the Scenes.mkv"
Once you have made all of these types of files go to Programs in xbmc and run the DvdExtras script.  It will search for all files in this format and create nfo files with the season, episode, and
title provided by the filename.  Then it will trigger a library update so that the xbmc scanner will include them in the library.


### XBMC File Exclusions
Since these are video files sprinkled in among all of your other video files we need to tell the xbmc scanner to ignore these files.  If we don't then the scanner will try and match
them up with one of the online sites and you probably won't be happy with the results.  To do this we just need to add some new regular expressions to the [advanced settings](http://wiki.xbmc.org/index.php?title=Advancedsettings.xml).
These are the settings that I added.
```xml
<video>
  <excludefromscan>
    <regexp>-extras-</regexp>
    <regexp>/Extras/</regexp>
  </excludefromscan>
  <excludetvshowsfromscan>
    <regexp>-extras-</regexp>
    <regexp>/Extras/</regexp>
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