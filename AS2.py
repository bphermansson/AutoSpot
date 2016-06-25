#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Upload changes to Github:
# git commit AS2.py
# git push origin master
# Update from Github
# git pull

# https://github.com/alastair/spotifile

import os
import logging
import urllib2
import threading
import sys
import unicodedata
import datetime
import signal
import time
import spotify
from time import sleep

# Keyboard input
import tty, termios

# Import file with settings (settings.py):
import settings

global online

# Get keyboard presses
# http://www.instructables.com/id/Controlling-a-Raspberry-Pi-RC-Car-With-a-Keyboard/?ALLSTEPS
# Not used
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def internet_on():
    print "Check connection"
    try:
        response=urllib2.urlopen('http://google.se',timeout=2)
        #print "On"
        return True
    except urllib2.URLError as err: pass
    #print "Off"
    return False

def on_logged_in(session, error_type):
    assert error_type == spotify.ErrorType.OK, 'Login failed'
    if debug:
	print "In on_logged_in, Logged in"
    logged_in.set()
    
def on_end_of_track(session):
    print "Track ended\n"
    nextTrack()

def contLoaded(session, error_type):
    global BoolcontLoaded
    print "Container loaded"
    BoolcontLoaded = True
    if container.is_loaded is True:
	cont_loaded_event.set()
    
def nextTrack():
    global trackindex
    global nooftracks
    global playlisturis
    global trackuri
    if debug: 
      print "In nextTrack: Pl has " + str(nooftracks) + " tracks. trackindex = " + str(trackindex)
      print "trackuri: " + str(trackuri)
    inttrack = int(trackindex)
    intnooftracks = int(nooftracks)
    if(inttrack<intnooftracks-1):
        inttrack+=1
        print "Trackindex: " + str(inttrack) + "/" + str(intnooftracks)
        #print playlisturis
        #dur = track.load().duration
        #print str(dur/1000) + " sec"
        # Set trackuri to next track in playlist
        trackuri=playlisturis[inttrack]
        if debug:
	  print "Next track: " + str(trackuri)
        trackindex=str(inttrack)
        play()
        #time.sleep(2)
        #print session.player.state
    
        # Debug: Jump to end of track to see end of track callback
        #session.player.seek(dur-100)
    else:
        print "End of playlist, go to next pl"
        changePl("next")
        
def prevTrack():
    global trackindex
    global nooftracks
    global inttrack
    global trackuri
    if debug:
      print "In prevTrack: Pl has " + str(nooftracks) + " tracks. trackindex = " + str(trackindex)
    inttrack = int(trackindex)
    if(inttrack>0):
	inttrack -= 1
        print "trackindex: " + str(inttrack) + "/" + str(nooftracks) 
        #print playlisturis[trackindex]
        trackuri=playlisturis[inttrack]
        if debug:
	  print "Prev track: " + str(trackuri)
        trackindex=str(inttrack)
        play()
    else:
        print "Start of playlist"
        
def changePl(dir):
    global playlistnr
    global trackindex
    global nooftracks
    global playlisturis
    global pl
    global trackuri
    trackindex = 0
    
    if debug:
      print dir
    # Next or previous playlist?
    if(dir=="next"):
        playlistnr+=1
    elif(dir=="prev"):
        playlistnr-=1
    else:
        print "Playlist change error"
    if debug:
      print "Playlist # " +str(playlistnr)
    pl = str(container[playlistnr]).split(":")
    if debug:
      print "New pl = " + str(pl)
    pluser = pl[2]
    pluri = pl[4].split("'")
    pl = pluri[0]
    if debug:
      print "New pl (short)= " + str(pl)

    #print pluser + pluri[0] # == phermansson5Lg5sAr6bKzEYCq8LbewLM
    # Should be like "'spotify:user:fiat500c:playlist:54k50VZdvtnIPt4d8RBCmZ'"
    getpluri = "spotify:user:" + pluser + ":playlist:" + pluri[0]
    #print getpluri
    playlist = session.get_playlist(getpluri)
    offline = playlist.offline_status
    if debug:     
	print "Offline: " + str(offline)	# 0 = not available offline 1 = Available offline
	print "spotonstatus: " + str(spotonstatus) # 1 = online 2 = offline
	if offline == 0 and spotonstatus == 2:	# Playlist not downloaded and we are offline - This means trouble!
		print "Cant play this. Not available offline"
	
	# DO SOMETHING ABOUT THIS SITUATION
      
    #print playlist
    curpl = unicodedata.normalize('NFKD', playlist.load().name).encode('ascii', 'ignore')
    if debug:
      print "curpl (real name): " + curpl
    
    # Load playlist:
    if debug:
      print "Load the playlist"
    loadPlaylist(getpluri, pl)
    
    # Create a list with the playlists tracks
    nooftracks = len(playlist.tracks)
    if debug:
      print str(nooftracks) + " tracks."
    playlisturis=[]
    for x in range(0, nooftracks):
        curtrack = str(playlist.tracks[x])
        curtrackuri = curtrack.split("'")
        playlisturis.append(curtrackuri[1])
    if debug:
      print "Playlist array created"
    #print playlisturis[1]
    
    """
    track = session.get_track( playlisturis[1]).load()
    #trackindex=0
    #print track
    trackname=track.load().name
    curtrack = unicodedata.normalize('NFKD', trackname).encode('ascii', 'ignore')
    print str(trackindex) + " " + curtrack
    
    dur = track.load().duration
    print str(dur/1000) + " sec"

    # Available offline?
    offline = playlist.offline_status
    if offline==0:
        offline_status="Available offline"
    else:
        offline_status="Not available offline"
    if gui=="tk":
      lblOffline["text"]=offline_status
    else:
      if debug:
	print offline_status
    
    # Set track variable and play the track
    """
    
    trackuri = playlisturis[0]
    trackindex=0
    play()

    #session.player.load(track)
    #session.player.play()
    #time.sleep(2)
    #print session.player.state
    
    # Debug: Jump to end of track to see end of track callback
    #session.player.seek(dur-100)

def play():
    global trackindex
    #global inttrack
    global artistname
    global trackname
    global trackofflinestatus, offlinetxt
    global trackindex
    global trackuri
    global spotonstatus
    global albumname
    if debug:
      print "In play, trackuri=" + str(trackuri)
      print "On/Offline status=" + str(spotonstatus)

    track = session.get_track(trackuri)
    
    album = str(track.album).split("'")
    albumname = session.get_album(album[1])
    albumname = albumname.load().name

    trackname=track.load().name
    dur = track.duration
    trackinfo = trackname.encode('utf-8')
    if debug:
	print "Track:" + str(trackindex) + "-" + trackinfo + " length:" + str(dur)

    # Get artist code
    artist=track.load().artists
#    if debug: 
#	    print "---In play, artistcode = " + str(artist)
    #print artist
    temp = str(artist).split(":")
    #print "temp: - " + str(temp)
    art = temp[2].split("'")
    #print art[0]
    artisturi="spotify:artist:" + art[0]
    artist = session.get_artist(artisturi)
    artistname = artist.load().name
    """artist = session.get_artist(
...     'spotify:artist:22xRIphSN7IkPVbErICu7s')
    artist.load().name"""
    curtrack = unicodedata.normalize('NFKD', trackname).encode('ascii', 'ignore')
    curartist = unicodedata.normalize('NFKD', artistname).encode('ascii', 'ignore')
    trackname = curtrack # Global var for Gui
    if debug:
	print "Artist: " + curartist + "- Track: " + curtrack +"-"+ str(trackindex)
	print "Album: " + albumname

    session.player.load(track)

    # Track available offline?
    trackofflinestatus = track.offline_status
    if trackofflinestatus == 0:
        offlinetxt="Not available offline"
    elif trackofflinestatus == 1:
        offlinetxt = "Waiting for download"
    elif trackofflinestatus == 2:
	offlinetxt = "Download in progress"
    elif trackofflinestatus == 3:
        offlinetxt = "Downloaded\n"
    else:
	offlinetxt = "Download error\n"
      
    if debug:
	print "Offline? " + str(trackofflinestatus) + " - " + offlinetxt
    
    # Can we play the track?
    if spotonstatus == 1 or trackofflinestatus == 3: 	# We are online or track is downloaded
	session.player.play()
    else:
	    if debug:
		    print "Track not available!"
    
    #status["text"]= "Playing"
    updateGui()

    # Debug: Jump to end of track to see end of track callback
    #session.player.seek(dur-100)

def playerPause():
    #status["text"]="Play/Pause"
    ps=session.player.state
    if (ps=="paused"):
        session.player.play()
    else:
        session.player.pause()
    updateGui()
    
def loadPlaylist(getpluri, pl):
    # Create a list with the playlists tracks
    # getpluri is full uri, pl is the playlist code

    global playlisturis
    global nooftracks
    global trackindex
    global playlist
    global lblOffline
    global curtrack
    global spotonstatus
    global errortext
    global plnameenc
    if debug:
      print "---In loadPlaylist---"
      print "getpluri=" + getpluri
      print "pl=" + str(pl)
      print "On/Offline status=" + str(spotonstatus)
    #playlist = session.get_playlist('spotify:user:fiat500c:playlist:54k50VZdvtnIPt4d8RBCmZ')
    #getpluri=spotify:user:phermansson:playlist:55BhUdMcydRRoBMnmbJsiU
    
    try:
      playlist = session.get_playlist(getpluri)
    except:
      if debug:
	print "Playlist load error"	# We couldnt load the playlist. Try the next one
	changePl(next)
    #playlist = session.get_playlist("spotify:user:phermansson:playlist:2goTnMEhmPyr3zyOYLNxJ1")
    #playlist = session.get_playlist("spotify:user:phermansson:playlist:6GVBKiGSWKAwJlVxPGxD9h")
    
    plnameenc = unicodedata.normalize('NFKD', playlist.load().name).encode('ascii', 'ignore')
    if debug:
      print "Playlist name: " + plnameenc
      print "Check offline status" 

    # Offline status
    offlinestatus = playlist.offline_status
    offlinetxt=""
    if offlinestatus == 0:
        offlinetxt="Not available offline"
    if offlinestatus == 1:
        offlinetxt = "Available offline"
    if offlinestatus == 2:
        offlinetxt = "Download in progress"
    if offlinestatus == 3:
        offlinetxt = "Waiting for download\n"
    #lblOffline["text"]= offlinetxt

    if debug:
      print "Offline? : " + str(offlinetxt)
      if spotonstatus == 4 and offlinestatus == 0:
	print "We are offline and this pl is NOT available offline. We are in trouble."
	errortext="Cant play this, not available offline"
	session.player.pause()
	while(0):
	  pass
      else: 
	errortext=""
      #print "Download completed: " + str(playlist.offline_download_completed)
      

    nooftracks = len(playlist.tracks)
    playlisturis=[]
    if debug:
      print "Tracks in current playlist:"
    for x in range(0, nooftracks):
        curtrack = str(playlist.tracks[x])
        curtrackuri = curtrack.split("'")
        playlisturis.append(curtrackuri[1])
        
        if debug:
	  print curtrackuri[1]
    #print playlisturis[1]
    
    """
    inttrack = int(trackindex)
    if debug: 
      print "Trackindex: " + str(inttrack) 
    
    track = session.get_track( playlisturis[inttrack]).load()
    #trackindex=0
    #print track
    trackname=track.load().name
    curtrack = unicodedata.normalize('NFKD', trackname).encode('ascii', 'ignore')
    print "Playlist load, Track: " + curtrack + ", trackindex=" + str(trackindex)
    play(curtrackuri[1])
    """
def pldownload():
    global pl
    global playlist
    global spotonstatus
    print "In pldownload"
    if spotonstatus <> 1:
	# Not online, cant download
	if gui=="tk":
		status["text"]= "Offline, cant download"
	elif debug:
		print "Offline, cant download"
	return
	
    if gui=="tk":
      status["text"]= "Going to download pl"
      lblError["text"] = errortext
    elif debug:
      print "Errortext: " + str(errortext)
      print "Going to download pl"
      print "Pl:" + str(pl)
    if playlist.offline_status == 0 and not spotonstatus == 4:
        playlist.set_offline_mode(offline=True)
        if debug:
	  print "offline=True"
    else:
        playlist.set_offline_mode(offline=False)
	if debug:
	  print "offline=False"
def offline_update(session):
    # Called when offline sync status is updated.
    global trackofflinestatus
    global curtrack
    global debug
    global trackuri
    global spotonstatus
    global offlinetext
    
    # If we go offline while downloading, the app hangs..?.
    
    tts = str(session.offline.tracks_to_sync)
    
    if debug:
	print "In offline_update, Offline sync status updated\n"
	print "Tracks left to download: " + str.rstrip(tts) + "\n"
	print "spotonstatus: " + str(spotonstatus) + "\n"
    """
     class spotify.offline.Offline(session)
        tracks_to_sync
     -> tts = session.offline.tracks_to_sync
     
     class spotify.Track(session, uri=None, sp_track=None, add_ref=True)
	 offline_status
     -> tos = session.Track.offline_status
    """
    
    #trackofflinestatus = track.offline_status
    
    # Is trackuri defined as global?
    if 'trackuri' in globals():
      if (trackuri):

	if debug:
	  print "In offline update - trackuri given"
	track = session.get_track(trackuri)
	tos = track.offline_status

	if debug:
	  print "Track offline status:" + str(tos)
      
	  #offlinestatus = playlist.offline_status
	  offlinestatus=tos
	  offlinetxt=""
	  if offlinestatus == 0:
		  offlinetxt="Not available offline"
	  if offlinestatus == 1:
		  offlinetxt = "Available offline"
	  if offlinestatus == 2:
		  offlinetxt = "Download in progress"
	  if offlinestatus == 3:
	      offlinetxt = "Waiting for download\n"

	  # Print and update gui
	  if debug:
	      print "Offline status" + str(offlinestatus) + ":" + offlinetxt
	  if gui=="tk":
	      lblOffline["text"]= offlinetxt
	  
      else:
	if debug:
	  print "Trackuri not defined yet"
def onoffline():
    print "In onoffline"
    #spotify.connection.Connection._allow_network=False
    #spotify.ConnectionType=1
    if session.connection.allow_network == True:
        session.connection.allow_network = False
    else:
	session.connection.allow_network = True
	
    #print "Conn state: " + str(session.connection.state)
    #session.connection._allow_network = False
    #print "New conn state: " + str(session.connection.state)
    if debug:
      print "Allow network= " + str(session.connection.allow_network)
      print session.connection.state
      
def loadplaylists():
    global container
    global BoolcontLoaded
    BoolcontLoaded = False
    # Load playlist container
    if debug:
      print "In loadplaylists"
    container = session.playlist_container
    spotonstatus=session.connection.state	# Online or not? 1=offline, 2=online

    # Load playlist data
    if debug:
      print "Wait while playlists are loaded, might take a while."

    container.load	# "Block until the playlist container?s data is loaded."
    
    if debug:
      print "Container load: " + str(container.is_loaded)
      #print "We are " + str(spotonstatus)

    # Wait for container loaded event to fire
    """cont_loaded_event.wait()
    c=0
    while (BoolcontLoaded == False):
	session.process_events()
	print "Wait for containers..." + str(c)
	print str(BoolcontLoaded)
	c+=1
    """
    print "Container loaded"
    print "You have " + str(len(container)) + " playlists."
    if (len(container))==0:
	    print "Error"
	    sys.exit()
    #print container
    v=0
    for items in container:
        left = str(items)[:14]
	#print left
	#print items
        contItem = str(items).split(":")
        # Exclude Playlist folder entries
        if not left=="PlaylistFolder":
            #print "Item: " + str(items)
            #print items
            contUri = contItem[4].split("'")
            contUriuri = contUri[0]
            #print "Item uri:"  + str(v) + "----" + str(contUriuri)
            localuri = str(items).split("'")
            playlist = session.get_playlist(localuri[1])
            #print str(playlist) + "---" + str(playlist.offline_status)
            
            if not playlist.offline_status == 0:
                print "localuri: " + str(localuri[1])

            v+=1

def conn_state_change(session):
    global lblSpotonline
    global onlinetext
    global spotonstatus
    
    spotonstatus=session.connection.state
    if (spotonstatus==0):
      onlinetext="Logged out"
    elif (spotonstatus==1):
      onlinetext="Online"
    elif (spotonstatus==2):
      onlinetext="Disconnected"
    elif (spotonstatus==3):
      onlinetext="Undefined"
    elif (spotonstatus==4):
      onlinetext="Offline"
    else:
      onlinetext="Error"
    if debug:
	print "Conn state changed, we are " + onlinetext + "\n"
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()

def cleanexit():
    # Save info
    global uri
    global trackindex
    global playlistnr
    global pl
    global curtrack
    global trackuri
    global log
    if debug:
	    print "In cleanexit, values to save:"
	    print "Username: " + username
	    print "Password: " + password
	    print "Playlist:" + str(pl) + "(" + str(playlistnr) + "), track " + str(trackindex)
	    print "Current track: " + str(trackuri)
	    print "Gui type: " + str(gui)
	    print "Debug: " + str(debug)
	    print "Log: " + str(log)
	    
    file = open("settings.py", "w")
    file.write("username=\"" + username+"\"\n")
    file.write("password=\"" + password+"\"\n")
    file.write("playlist=\"" + str(pl)+"\"\n")
    file.write("trackindex=\"" + str(trackindex)+"\"\n")
    file.write("Current_track=\"" + str(trackuri)+"\"\n")
    file.write("playlistnr=\"" + str(playlistnr)+"\"\n")
    file.write("guitype=\"" + str(gui)+"\"\n")
    file.write("debug=" + str(debug)+"\n")
    file.write("log=" + str(log)+"\n")

    file.close()
    if debug: 
	print "Bye!"
    if gui=="ILI9341":
	display.clear()
    	draw_rotated_text(disp.buffer, 1, 'Bye!', (posline1), 90, font, fill=(255,0,0))	

    sys.exit(1)

def keyinput(event):

    key = event.char
    if key.upper() == '6':
        nextTrack()
    elif key.upper() == '4':
        prevTrack()
    elif key.upper() == '8':
        changePl("next")
    elif key.upper() == '2':
        changePl("prev")
    elif key.upper() == 'Q':
        cleanexit()
    elif key.upper() == '1':
        pldownload()
    elif key.upper() == '5':
        playerPause()
    elif key.upper() == '3':
        onoffline()

def updateGui():
    global artistname, onlinetext, offlinetext, trackname, errortext, plnameenc, albumname, lblOffline
    global lstatus
    #print "In updateGui"

    # Are there offline tracks to sync?
    #print "Sync status: " + str(session.offline.sync_status)

    #class spotify.offline.Offline(session)
    #    tracks_to_sync
    
    tts=session.offline.tracks_to_sync
    #print "Tracks to sync: " + str(tts)
    #print "No of offline pls: " + str(session.offline.num_playlists)
    
    if tts>0:
        dltext=" " + str(tts) + " left"
        print str(dltext)
	#if gui=="tk":
	#	lblOffline["bg"]='Red'
		
    else:
        dltext=""
	#if gui=="tk":
	#	lblOffline["bg"]='Yellow'
    
    #sync_in_progress = session.offline.sync_status
    #print sync_in_progress

    tracknamelength = len(trackname)
    #print "Trackname has " + str(tracknamelength) + " chars"
    if tracknamelength>20:
      trackname=trackname[0:20]	# Cut trackname
      
    #ti=int(trackindex)+1	# For correct display. Trackindex starts at 0 but we want it displayed as track # 1
    ti=int(trackindex)
    ti+=1
    ps=session.player.state
    if debug:
	print "Update graphical display"
	print "Artistname: " + str(artistname) 
	print "Playlistname: " + str(plnameenc)
	print "Albumname: " + str(albumname)
	print "Offline: " + str(offlinetxt + dltext)
	print "Spotonline: " + str(onlinetext)
	print "Error: " + str(errortext)
	print "dltext: " + str(dltext)
	print "Tracks to download: " + str(tts)

	
    if gui=="tk":
	"""lblArtist["text"]= artistname
	lblAlbum["text"]= albumname
	lblTrack["text"]= str(ti).zfill(2) + "-" + trackname    # zfill adds a leading 0
	lblSpotonline["text"]=onlinetext
	lblOffline["text"]= offlinetxt + dltext
	lblError["text"] = errortext
	status["text"]=ps
	"""
	global lstatus
	lstatus.set("Updategui")

	# Update Gui every second
	root.after(1000, updateGui)
    elif gui=="ILI9341":
	disp.clear()
	draw_rotated_text(disp.buffer, 1, "Artist: " + artistname, (posline1), 90, font, fill=(255,0,0))	
	draw_rotated_text(disp.buffer, 2, "Album: " + albumname, (posline2), 90, font, fill=(255,0,0))	
	draw_rotated_text(disp.buffer, 3, "Track: " + trackname, (posline3), 90, font, fill=(255,0,0))	
	draw_rotated_text(disp.buffer, 4, "PL: " + plnameenc, (posline4), 90, font, fill=(255,0,0))	
	draw_rotated_text(disp.buffer, 5, onlinetext, (posline5), 90, font, fill=(255,0,0))	
	draw_rotated_text(disp.buffer, 6, offlinetxt, (posline6), 90, font, fill=(255,0,0))	
	draw_rotated_text(disp.buffer, 7, ps, (posline7), 90, font, fill=(255,0,0))	
	
	#
	# Add line for off/online
	#
	
	# Update display
	disp.display()


def draw_rotated_text(image, linenr, text, position, angle, font, fill=(255,255,255)):
	# For graphical display
	# Get rendered font width and height.
	draw = ImageDraw.Draw(image)
	width, height = draw.textsize(text, font=font)
		
	# Adjust label positions so text starts at left border 
	# Make a list of the position tuple, change value, and make a new tuple
	lst = list(position)
	
	# Special treat for line 6
	if linenr==6:
		# This line shall have a fixed position
		print "line6"
		lst[1]=10
	else:
		lst[1] = 320-width - 5
	if lst[1]<0:
		lst[1]=0
	
	position = tuple(lst)
	
	#print "Line: " + str(linenr)
	#print "Position: " + str(position)
	
	"""print "pos0: " + str(position[0])
	print "pos1: " + str(position[1])
	print "Width: " + str(width)"""
	
	# Create a new image with transparent background to store the text.
	textimage = Image.new('RGBA', (width, height), (0,0,0,0))
	# Render the text.
	textdraw = ImageDraw.Draw(textimage)
	textdraw.text((0,0), text, font=font, fill=fill)
	# Rotate the text image.
	rotated = textimage.rotate(angle, expand=1)
	# Paste the text into the image, using it as a mask for transparency.
	image.paste(rotated, position, rotated)

def on_closing():
    cleanexit()
    if gui=="tk":
	root.destroy()

if __name__ == '__main__':
    #logging.basicConfig(level=logging.INFO)
    global playlistnr
    global pl, artistname, trackindex, trackname, session, offlinetxt, container
    global lblSpotonline, lblOffline, curtrack, debug, log, trackuri
    global lblArtist
    global lstatus
    artistname="Artist"
    trackindex=0
    trackname="Trackname"
    offlinetxt=""
    curtrack=""
    
    """
    # Check where we are
    path = os.getcwd()
    #print path
    # The current dir is Autospot?
    curdirArr = path.split("/")
    levels=len(curdirArr)
    #print levels
    curdir=curdirArr[levels-1]
    #print curdir
    if (curdir == "AutoSpot"):
        print "ok"
    else:
        os.chdir("AutoSpot")
    """   
    
    print "Welcome to Autospot"
    
    # Debug mode?
    debug = settings.debug
    log = settings.log
    if debug:
	print "Debug mode"
    if log:
      print "Log mode enabled"	# Used for debugging, gives more info
      import logging
      logging.basicConfig(level=logging.DEBUG)
    
    # Which gui to use?
    gui = settings.guitype
    if debug:
	print "Use gui: "+gui

    # Create Spotify session
    # Assuming a spotify_appkey.key in the current dir
    session = spotify.Session()
    spotonline=session.connection.state

    if gui=="tk":
        # Gui, uses Tkinter
	try:
		from Tkinter import *
        except:
		print "Tkinter not available"
		print "(sudo apt-get install python-tk)"
		sys.exit()
	root = Tk()
        root.minsize(width=320, height=240)
        root.maxsize(width=320, height=240)
        root.wm_title("Autospot")
        infotext = "6-Next tr 4-Prev tr 8-Next Pl 2-Prev pl 1-Download 5-Pause 3-On/Offline q-Quit"
    elif gui=="text":
	        infotext = "6-Next tr 4-Prev tr 8-Next Pl 2-Prev pl 1-Download 5-Pause 3-On/Offline q-Quit"
	        print infotext    
    elif gui=="ILI9341":
	# https://learn.adafruit.com/user-space-spi-tft-python-library-ili9341-2-8/usage
	from PIL import Image
	from PIL import ImageDraw
	from PIL import ImageFont
	import Adafruit_ILI9341 as TFT
	import Adafruit_GPIO as GPIO
	import Adafruit_GPIO.SPI as SPI
	
	if debug:
		print "Setting up graphical display"
	
	# Set up display
	DC = 18
	RST = 23
	SPI_PORT = 0
	SPI_DEVICE = 0
	# Create TFT LCD display class.
	disp = TFT.ILI9341(DC, rst=RST, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE, max_speed_hz=64000000))

	# Initialize display.
	disp.begin()
	disp.clear()
	image = disp.buffer
	font = ImageFont.truetype('OstrichSans-Heavy.otf', 30)

	posline1=(10,3)	# Pos y,x, vertical/horizontal
	posline2=(50,3)
	posline3=(90,3)
	posline4=(130,3)
	posline5=(170,3)
	posline6=(210,3)
	posline7=(210,3)
	
	draw_rotated_text(disp.buffer, 1, 'Autospot 1.0', (posline1), 90, font, fill=(255,0,0))	
	disp.display()
	
	if debug:
		print "Done setting up graphical display"
	
    # Check for internet connection
    # Use libspotifys online-check instead
    """
    try:
        online = internet_on()
        if online == True:
            onlinestatus="online"
        else:
            onlinestatus="offline"
        print "Online?: " + onlinestatus
    except:
        pass
    """

    # Process events in the background
    loop = spotify.EventLoop(session)
    loop.start()

    # Events for coordination
    logged_in = threading.Event()
    logged_out = threading.Event()
    end_of_track = threading.Event()
    cont_loaded_event = threading.Event()

    # Register event listeners
    session.on(spotify.SessionEvent.LOGGED_IN, on_logged_in)
    session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)
    session.on(spotify.PlaylistContainerEvent.CONTAINER_LOADED, contLoaded)
    session.on(spotify.SessionEvent.OFFLINE_STATUS_UPDATED,offline_update)
    session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, conn_state_change)
    # Create audio sink
    if debug:
	print "Check audio subsystem:"
    try:
        audio_driver = spotify.AlsaSink(session)
	if debug:
		print "Audio ok"
    except ImportError:
        #logger.warning(
        #    'No audio sink found; audio playback unavailable.')
	if debug:
		print "No audio sink found; audio playback unavailable."
		if gui=="ILI9341":
			draw_rotated_text(disp.buffer, 1, "Audio system error, bye!", (posline1), 90, font, fill=(255,0,0))	
		elif gui=="tk":
			infotext = "Audio system error, bye!"

        sys.exit()
        
    try:
        username = settings.username
        password = settings.password
        if debug:
		print "User credentials from settings file: " + username + "-" + password
    except: 
        if debug:
		print "No username or password given in settings.py, fix that!"
        sys.exit(0)
      
    # Login
    #session.login(username, password)
    #logged_in.wait()

    remUser = session.remembered_user_name
    if debug:
	print "Remembered user: " + str(remUser)
    if not remUser:
      print "Wait for login " + username 
      session.login(username, password, remember_me=True)
      logged_in.wait()
    else:
      session.relogin()	# Spotify remembers us, just relogin
      logged_in.wait()
    if gui=="text":
	print str(session.user_name) + " is logged in"
    
    """ 'Wait til we are online'... What if we are not connected to the internet? 
    Stupid function...
    
    # Wait til we are online
    spotonstatus=session.connection.state
    if spotonstatus == 0:
	text="Logged out"
    elif spotonstatus == 1:
	text="Logged in"
    elif spotonstatus == 2:
	text="Disconnected"
    elif spotonstatus == 3:
	text="Undefined"
    elif spotonstatus == 4:
	text="Offline"
			
    while not (spotonstatus==1):	# '1' = logged in
      spotonstatus=session.connection.state
      if debug:
	print "onlinestatus: " + str(spotonstatus) + " - " + text
      sleep(1)

    if debug:
	print "Logged in"
"""	
	
    # Get saved track
    try: 
      trackuri=settings.Current_track
    except:
      print "No track saved"
      
    """
    # Load playlist container
    container = session.playlist_container
    container.load
    while not container.load:
            pass
    print "Container loaded"
    print "You have " + str(len(container)) + " playlists."
    """
    
    # Load users playlists
    if debug:
	print "Load playlists"
    loadplaylists()
    
    if debug:
      print "Playlists loaded"
      print "Trackindex: " + str(trackindex)
    
    # Get saved playlist
    try:
        pl = settings.playlist
        trackindex = settings.trackindex
        strPlaylistnr=settings.playlistnr
        playlistnr = int(strPlaylistnr)
        if debug:
		print "We have a saved playlist"
		print "Playlist" + str(pl) + ", (" + str(playlistnr) + "), track " + str(trackindex)
    except: 
        if debug:
		print "Unexpected error:", sys.exc_info()[0]
		print "No playlist saved!"
        pl=""
        trackindex=0
        playlistnr=0
        # Find the first track in the first playlist

    # First playlist
    #print "Container:" + str(container[1]) # == Playlist(u'spotify:user:phermansson:playlist:2Zkhao8VTWPfVD1oeha5I4')
    if not pl:
        global uri
        # No saved playlist, get the first
        # Form data for get_playlist
        playlistnr = 1
        pl = str(container[playlistnr]).split(":")
        pluser = pl[2]
        pluri = pl[4].split("'")
        uri = pluri[0]
        if gui=="text":
		print "Uri:" + str(uri)
        #print pluser + pluri[0] # == phermansson5Lg5sAr6bKzEYCq8LbewLM
        # Should be like "'spotify:user:fiat500c:playlist:54k50VZdvtnIPt4d8RBCmZ'"
        getpluri = "spotify:user:" + pluser + ":playlist:" + pluri[0]
        #print getpluri
    else: 
        getpluri = "spotify:user:" + username + ":playlist:" + pl
        if debug:
		print "Using saved playlist: " + getpluri + " (Saved: " + pl + ")"
		print "Trackindex: " + str(trackindex)
    
    #getpluri is the current playlist
    if debug:
      print "Load the saved or the first playlist"
      print "getpluri, pl: " + str(getpluri) + " - " + str(pl)
    loadPlaylist(getpluri, pl)
    
    trackuri = playlisturis[int(trackindex)]
    if debug:
      print "Going to play " + str(trackuri) 
    play()
    

    if gui=="tk":
        # Gui elements
	
	#label1 = Label(root, text="prompt", width=20)
	#v = StringVar()
	#Label(label1, textvariable=v).pack()
	#v.set("New Text!")
	linfo= StringVar()
	lspotonline= StringVar()
	lstatus= StringVar()
	lartist= StringVar()
	lalbum= StringVar()
	ltrack= StringVar()
	loffline= StringVar()
	lerror= StringVar()
	
        lblInfo = Label(root,textvariable=linfo,fg='White',bg='Grey',font=("Helvetica", 10), wraplength=300, justify=LEFT)
        lblInfo.place(width=320, height=40)
        lblInfo.pack(fill=X, side=TOP)

        lblSpotonline = Label(root,textvariable=lspotonline,fg='Black',bg='White',font=("Verdana", 12))
        lblSpotonline.pack(fill=X, side=TOP)

        lblStatus = Label(root,textvariable=lstatus,fg='Black',bg='White',font=("Verdana", 16))
        lblStatus.pack(fill=X, side=TOP)

        lblArtist = Label(root,textvariable=lartist,fg='Black',bg='White',font=("Verdana", 20))
        lblArtist.pack(fill=X, side=TOP)
 
	lblAlbum = Label(root,textvariable=lalbum,fg='Black',bg='White',font=("Verdana", 20))
        lblAlbum.pack(fill=X, side=TOP)
	
        lblTrack = Label(root,textvariable=ltrack,fg='Black',bg='White',font=("Verdana", 14))
        lblTrack.pack(fill=X, side=TOP)

        lblOffline = Label(root,textvariable=loffline,fg='Black',bg='Yellow')
        lblOffline.pack(fill=X, side=TOP)

        lblError = Label(root,textvariable=lerror,fg='Black',bg='Yellow')
        lblError.pack(fill=X, side=TOP)
        
	lstatus.set("Welcome")
	
        # Keyboard input
        root.bind('<Key>', keyinput)
        # Update gui
        root.after(1, updateGui)

        # When window is closed
        root.protocol("WM_DELETE_WINDOW", on_closing)

        #Start gui
        # Main loop
        root.mainloop()

    elif (gui=="text") or (gui=="ILI9341"):    
	    # Infinite loop with keyboard input processing
	    #     infotext = "6-Next tr 4-Prev tr 8-Next Pl 2-Prev pl 1-Download 5-Pause 3-On/Offline q-Quit"

	    while True:
		char = getch()
		print char
		if(char == "6"):
		    nextTrack()
		if(char == "4"):
		    prevTrack()
		if(char == "8"):
		    changePl("next")
		if(char == "2"):
		    changePl("prev")
		if(char == "q"): 
		    # Quit
		    cleanexit()
		if(char == "1"):
		    # Download pl
		    pldownload()	
		if(char == "3"):
		    # Change online/offline mode
		    onoffline()
		if(char == "5"):           
		    # Pause player 
		    playerPause()
		

