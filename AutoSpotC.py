#!/usr/bin/env python3
# -*- coding: iso-8859-1 -*-

# Upload changes to Github:
# git commit -a
# git push origin master
# git push origin btnctrl
# Update from Github
#  git pull

from __future__ import unicode_literals
#from future import standard_library
#standard_library.install_aliases()
from builtins import str
from builtins import object
import cmd
import logging
import threading
import sys
import unicodedata
import datetime
import signal
import spotify
#import curses
# To load config file
import configparser
import urllib.request, urllib.error, urllib.parse

# LCD
#import os
#os.system("export QUICK2WIRE_API_HOME=/home/pi/AutoSpot/quick2wire-python-api")
#os.system("export PYTHONPATH=$PYTHONPATH:$QUICK2WIRE_API_HOME")
#from i2clibraries import i2c_lcd
import quick2wire.i2c as i2c
from i2clibraries import i2c_lcd

# Physical buttons
# Ref: https://www.cl.cam.ac.uk/projects/raspberrypi/tutorials/robot/buttons_and_switches/
#import RPi.GPIO as GPIO

# Try RPIO instead, may work with curses
# http://pythonhosted.org/RPIO/
#import RPIO

import time
prev_input = 0

global curplaylist
global playlist
global cleantrack, trackindex, tracks
global username, password, autoplay
global curtrack
global selPlaylist
global nooftracks
global online
global uri
uri=""
global ttpsreal
ttpsreal=""
global savedtrack
savedtrack=""
selPlaylist = 0

global pausstate
pausstate=True

# Null output for hiding output
class NullDevice(object):
    def write(self, s):
        pass

def initApp(self):
    print("In initApp")
  # Logged in?
  # if self.session.connection.state is spotify.ConnectionState.LOGGED_IN:
  # print "Logged in"
  #else :
    if session.connection.state is spotify.ConnectionState.LOGGED_OUT:
        print ("Login failed, check your settings")
        sys.exit()
  # Last played playlist
    global uri
    print ("Last playlist:" + uri)
    print ("Last track: " + savedtrack)

  # Necessary?
  #pl = self.session.playlist_container
  #pl.load()
  
        #print "pl:" + str(pl)
        # Trigger for playlists loaded event
        # What to do when playlists are loaded?
  #pl.on(
  #    spotify.PlaylistContainerEvent.CONTAINER_LOADED, self.on_container_loaded)



  # Wait until playlists has loaded
  #while True:
  #    if cloaded == 1:
  #        print "Playlists loaded, cloaded=1"
  #        break

def do_play():
        #stdscr.clear()
        #stdscr.addstr("In do_play\n")
        global ttpsreal
        global pl
        #print "ttpsreal: " + str(ttpsreal)
        track = session.get_track(ttpsreal)

        #curartist = unicodedata.normalize('NFKD', track.artists).encode('ascii','ignore')
        curartist = str(track.artists).split("'")
        curartistreal = curartist[1]
        #print "curartistreal: " + curartistreal
        artist = session.get_artist(curartistreal)
        curtrack = unicodedata.normalize('NFKD', track.name).encode('ascii', 'ignore')

        # Get playlist name 
        playlist = session.get_playlist(pl[1])
        curplaylist = unicodedata.normalize('NFKD', playlist.name).encode('ascii', 'ignore')
        
        # Clear and print
        nowplaying = unicodedata.normalize('NFKD', artist.load().name).encode('ascii', 'ignore')

        #stdscr.addstr("Now playing: " + nowplaying + " - " + curtrack + "\n")
        #stdscr.addstr("Track #: " + str(trackindex) + "\n")
        ctrk =  curtrack.decode("utf-8")
        nply = nowplaying.decode("utf-8")
        print ("Now playing: " + nply + " - " + ctrk + "\n")
        print ("Track #: " + str(trackindex) + "\n")   
        lcd.clear()
        lcd.setPosition(1, 0)
        lcd.writeString(nply)
        lcd.setPosition(2, 0)
        lcd.writeString(ctrk)

        pl = str(container[playlistindex]).split("'")

        #stdscr.addstr("Playlist: " + str(pl[1]) + "\n" + curplaylist + "\n")
        #stdscr.addstr("Playlistindex: " + str(playlistindex) + "\n")
        

        track.load().name
        session.player.load(track)
        while not (track.is_loaded):
            pass
        #stdscr.addstr ("Track loaded\n")

        #stdscr.addstr ("Press a key")
        # Debug, wait for keypress
        #while stdscr.getch() == "":
        #    pass

        session.player.play()

        # Debug, wait for keypress
        #while stdscr.getch() == "":
        #    pass

        # Get & print track duration
        dur = track.duration
        d = datetime.timedelta(milliseconds=dur)
        strd = str(d)
        strdm = strd.split(":", 1)
        #print "Duration: " + str(dur)
        #stdscr.clear()
        #stdscr.addstr("Track length: " + str(strdm[1]) + "\n")

        playlist = session.get_playlist(pl[1])
        curplaylist = unicodedata.normalize('NFKD', playlist.name).encode('ascii', 'ignore')
        # Available offline?
        offline = playlist.offline_status
        #stdscr.addstr("Playlist: " + curplaylist + " " + str(offline) + "\n")
        
        if offline == 0:
             print ("Not available offline\n")
            #stdscr.addstr ("Not available offline\n")
        if offline == 1:
             print ("Available offline\n")
            #stdscr.addstr ("Available offline\n")
        if offline == 2:
            #stdscr.addstr ("Download in progress\n")
            print ("Download in progress\n")
        if offline == 3:
            #stdscr.addstr ("Waiting for download\n")
            print ("Waiting for download\n")

        # Are we off- or online?
        #stdscr.addstr ("Online = " + str(internet_on()))
            
        #stdscr.refresh()

        # Move to end to test next track function
        # seekto = dur - 5000
        # session.player.seek(seekto)

 

def do_loaduserspl():
        print ("Load users playlists")
        global container
        container = session.playlist_container
        
        #print container.is_loaded
        #print "In loaduserspl, playlists loaded"
        #print container.is_loaded
        print ("Load pl")
        # 'load' dont work if it aint stored or printed, so we store it in a temp variable 
        
        # Hide output
        original_stdout = sys.stdout  # keep a reference to STDOUT
        sys.stdout = NullDevice()
        print (container.load())
        sys.stdout = original_stdout  # turn STDOUT back on
  
        while not (container.is_loaded):
            pass
        print ("Ok")
        print ("Container loaded=")
        print (container.is_loaded)

def do_read_settings(line):
        # Load & read configuration
        # Settings are stored in a file called "settings".
        # Example:
        # [Spotify]
        # username=<Spotify username>
        # pass=<Spotify password>

        #print "Load"
        config = configparser.ConfigParser()
        try:
            print ("Load settings!")
            config.read("settings.txt")
        except:
            print ("Settings file not found")
            sys.exit()
        print (config.sections())

        try:
            global uri
            uri = ""
            options = config.options("Spotify")
            global username
            try:
                username = config.get("Spotify", "username")
            except:
                print ("No username given")
            global password
            password = config.get("Spotify", "pass")
            print ("Credentials: " + username + ":" + password)
            global autoplay
            try:
                autoplay = config.get("General", "autoplay")
                print ("Autoplay: " + autoplay)
            except:
                print ("No autoplay setting found")

            global savedtrack
            global playlistnr

            try:
                uri = config.get("CurrentTrack", "playlist")
                print ("Get playlist...")
            except:
                #uri = "spotify:user:phermansson:playlist:7JaJFymSwbFcceatOd40Af"
                pass
            try:
                savedtrack = config.get("CurrentTrack", "track")

            except:
                pass
            #savedtrack = "spotify:track:583jvp9iPtaOphRa74h0A8"

            #global trackindex
            #trackindex = int(Config.get("CurrentTrack", "trackindex"))
            #try:
            # playlistnr = int(Config.get("playlist", "playlistnr"))
            #except:
            # "No playlistnumbed saved"
            # playlistnr = 0
        except:
            print ("Error reading settings")
            sys.exit(0)

        if len(uri)==0:
            print ("No uri saved")
            global nouri
            nouri = 1
        else:
            nouri = 0
        if len(savedtrack)==0:
            print ("No track saved")
        global notrack
        notrack = 1

def on_connection_state_changed(session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            print ("Logged in")
            logged_in.set()
            logged_out.clear()
        elif session.connection.state is spotify.ConnectionState.LOGGED_OUT:
            logged_in.clear()
            logged_out.set()

def on_end_of_track(session):
        # global trackindex
        # global tracks
        # global nooftracks
        #stdscr.clear()
        #stdscr.addstr("End of track")
        do_next()

def on_logged_in(session):
        pass
  
#class Commander(cmd.Cmd):
    # doc_header = 'Commands'
    # prompt = 'spotify> '
    # logger = logging.getLogger('shell.commander')
"""
   def __init__(self):
        print "Welcome to Autospot \nCommands:"
        print "next - Next track"
        print "prev - Previous track"
        print "nextpl - Next playlist"
        print "prevpl - Previous track"
        print "set_offline - Make current playlist available offline"
        print "Exit - Save status, stop & exit"
        print "offstatus - Check offline status for current playlist\n"
  
  online = internet_on()
  if online == True:
    onlinestatus="online"
  else:
    onlinestatus="offline"

        cmd.Cmd.__init__(self)
        self.logged_in = threading.Event()
        self.logged_out = threading.Event()
        self.logged_out.set()
        self.session = spotify.Session()
        self.event_loop = spotify.EventLoop(self.session)
        self.event_loop.start()
        self.session.on(
            spotify.SessionEvent.CONNECTION_STATE_UPDATED,
            self.on_connection_state_changed)
        self.session.on(
            spotify.SessionEvent.END_OF_TRACK, self.on_end_of_track)
        self.session.on(
            spotify.SessionEvent.LOGGED_IN, self.on_logged_in)
  
"""
# TODO Add 'nouri=1' and 'notrack=1' to settings_editthis

 
def do_listoffline(list):
  print ("You have " + str(len(container)) + " playlists.")
  c=0
  for s in container:
    #print str(container[c])
    
    pl = str(container[c]).split("'")
    #print "Next pl is: (" + str(c) + ") - " + pl[1]
    pl.load().name
    offline = pl.offline_status
    #stdscr.addstr (offline)
    c+=1
      
def do_set_offline():
        "Set playlist offline"
        global playlist
        #stdscr.addstr ("Pl to set offline: " + str(playlist))
        #stdscr.addstr ("Offline: " + str(playlist.offline_status))
        if playlist.offline_status == 0:
            #stdscr.addstr ("Ok, downloading")
            playlist.set_offline_mode(offline=True)
        else:
            #stdscr.addstr ("Removed from harddisk")
            playlist.set_offline_mode(offline=False)

def do_offstatus(list):
        "Offline status"
        #stdscr.addstr ("Downloaded: " + str(playlist.offline_download_completed) + "%")

        offline = playlist.offline_status
        #sprint offline
        if offline == 0:
            #stdscr.addstr ("Not available offline")
            print ("Not available offline")
        if offline == 1:
            #stdscr.addstr ("Available offline")
            print ("Available offline")
        if offline == 2:
            #stdscr.addstr ("Download in progress")
            print ("Download in progress")
        if offline == 3:
            #stdscr.addstr ("Waiting for download")
            print ("Waiting for download\n")
def do_nextpl():
        "Next playlist"
        global playlistindex
        global container
        global playlist
        # print "Current playlistindex: " + str(playlistindex)

        #stdscr.addstr ("You have " + str(len(container)) + " playlists.")
        
        playlistindex += 1

        if (playlistindex+1>len(container)):
            playlistindex=0

        pl = str(container[playlistindex]).split("'")
        #print "Next pl is: (" + str(playlistindex) + ") - " + pl[1]

        playlist = session.get_playlist(pl[1])
        curplaylist = unicodedata.normalize('NFKD', playlist.name).encode('ascii', 'ignore')

        # Available offline?
        ploffline = playlist.offline_status
        rpionline = internet_on()
        ofstat = ""
        if ploffline == 1:
            ofstat = "*"
        if (ploffline!=1 and rpionline==False):
            # Playlist not available offline, and we are offline...
            #stdscr.addstr("Playlist not available\n")
            print ("Playlist not available\n")


        #print "Playlist name: " + curplaylist + ofstat

        # Find first track in new playlist
        playlist.load().name
        while not (playlist.is_loaded):
            pass
        #print "Playlist loaded"

        # Get first track of new playlist
        #print str(playlist.tracks[0])
        firsttrack = str(playlist.tracks[0])
        firsttrackar = firsttrack.split("'")
        #print "First track of new list: " + firsttrackar[1]
        global ttpsreal
        ttpsreal = firsttrackar[1]
        global trackindex
        trackindex = 0
        global uri
        realuri = str(playlist)
        ruri = realuri.split("'")
        uri = ruri[1]
        #print "In nextpl: uri=" + uri
        #uri = playlist
        # ... and play it
        do_play()


def do_prevpl():
        #stdscr.clear()
        #stdscr.addstr("In do_prevpl\n")
        #"Previous playlist"
        global playlistindex
        global playlist
        #stdscr.addstr ("Current playlistindex: " + str(playlistindex)+"\n")
        #stdscr.refresh()

        playlistindex -= 1

        #stdscr.addstr ("New playlistindex: " + str(playlistindex)+"\n")


        pl = str(container[playlistindex]).split("'")
        #stdscr.addstr ("Current pl is: " + pl[1] + "\n")

        playlist = session.get_playlist(pl[1])
        curplaylist = unicodedata.normalize('NFKD', playlist.name).encode('ascii', 'ignore')

        # Available offline?
        offline = playlist.offline_status
        ofstat = ""
        if offline == 1:
            ofstat = "*"

        #stdscr.addstr("Playlist name: " + curplaylist + ofstat +"\n")
        #print "Playlist name: " + curplaylist + ofstat

        # Find first track in new playlist
        playlist.load().name
        while not (playlist.is_loaded):
            pass
        #stdscr.addstr("Playlist loaded" +"\n")


        # Get first track of new playl
        #print str(playlist.tracks[0])
        firsttrack = str(playlist.tracks[0])
        firsttrackar = firsttrack.split("'")
        #stdscr.addstr("First track of new list: " + firsttrackar[1]+"\n")
        #stdscr.addstr("Playlist name: " + curplaylist + ofstat +"\n")

        global ttpsreal
        ttpsreal = firsttrackar[1]
        global trackindex
        trackindex = 0
        global uri
        realuri = str(playlist)
        ruri = realuri.split("'")
        uri = ruri[1]

        #print "In prevpl: uri=" + uri
        #uri = playlist
        # ... and play it
        #stdscr.addstr ("Press a key before play starts")
        # Debug, wait for keypress
        #while stdscr.getch() == "":
        #    pass

        do_play()

  

def on_connection_state_changed(session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            logged_in.set()
            logged_out.clear()
        elif session.connection.state is spotify.ConnectionState.LOGGED_OUT:
            logged_in.clear()
        logged_out.set()

    # print container.is_loaded
    #print "Loaded pls"

"""
  def do_whoami(self, line):
    "whoami"
    if self.logged_in.is_set():
      self.logger.info(
      'I am %s aka %s. You can find me at %s',
      self.session.user.canonical_name,
      self.session.user.display_name,
      self.session.user.link)
    else:
      self.logger.info(
      'I am not logged in, but I may be %s',
      self.session.remembered_user)
"""
def on_container_loaded(session):
        global cloaded
        #print "Container loaded"
        cloaded = 1

def on_end_of_track(session):
        # global trackindex
        # global tracks
        # global nooftracks

        #print "End of track"
        do_next()

def on_logged_in(session, dummy):
        pass


def do_next():
        "Next track"
        global trackindex
        global playlist
        global ttpsreal
        global nooftracks
        global uri
        #stdscr.addstr("Next track")

        #print "uri=" + str(uri)

        # Check if at end of playlist
        if trackindex < nooftracks:
            #stdscr.addstr("Next track, index: " + str(trackindex) )
            #print "Next track"
            trackindex += 1
            #print "Trackindex: " + str(trackindex)
            playnext()
        else:
            #stdscr.addstr("End of playlist")
            #print "End of playlist"
            # Stop playback
            session.player.play(False)
            trackindex = 0
            playnext()

def do_prev():
        "Previous track"
        global trackindex
        global playlist
        global ttpsreal
        global nooftracks

        # Check if at end of playlist
        if trackindex > 0:
            #print "Next track"
            trackindex -= 1
            #print "Trackindex: " + str(trackindex)
            playnext()

        else:
            #print "Beginning of playlist"
            # Stop playback
            session.player.play(False)
            trackindex = 0
            playnext()

def do_exit():
        "Stop music and exit"
        print ("Bye!")
        cleanexit()

def playnext():
  global trackindex
  global ttpsreal
  global playlist
  #print trackindex
  ttp = str(playlist.tracks[trackindex])
  ttps = ttp.split("'")
  ttpsreal = ttps[1]
  #print "Track to play: " + str(ttpsreal)
  #stdscr.addstr("Track:"+ str(ttpsreal) + "\n")
  uri = str(ttpsreal)
  do_play()

def do_pause():
    global pausstate
    if pausstate==False:
        #stdscr.addstr("Play")
        #session.player.pause()
        pausstate = True
    else:
        #stdscr.addstr("Pause")
        pausstate = False
    session.player.play(pausstate)
        
#print "We received a 'on_logged_in'"
def showinfo(list):
    print ("Time!")
    
def internet_on():
    try:
        response=urllib.request.urlopen('http://74.125.228.100',timeout=20)
        return True
    except urllib.error.URLError as err: pass
    return False

def gpio_callback(gpio_id, val):
    print("gpio %s: %s" % (gpio_id, val))
    if (gpio_id == 27 and val == 1):
        print ("Next") 	
        do_next()
    if (gpio_id == 9 and val == 1):
        print ("Nextpl") 	
        do_nextpl()
    if (gpio_id == 10 and val == 1):
        print ("Prev") 	
        do_prev()
    if (gpio_id == 22 and val == 1):
        print ("Prevpl") 	
        do_prevpl()
       #stdscr.addstr("gpio %s: %s" % (gpio_id, val))
       #stdscr.addstr("Button")


def cleanexit():
    #curses.nocbreak()
    #stdscr.keypad(0)
    #curses.echo()
    #curses.endwin()
    print ("Do a clean exit")
    print ("Current playlist " + str(uri))
    print ("Current track: " + str(ttpsreal))
    # Save info
    from configparser import SafeConfigParser
    config = SafeConfigParser()
    config.read('settings.txt')
    # Is there a CurrentTrack section already?
    try:
        config.add_section('CurrentTrack')
    except:
        pass
    config.set('CurrentTrack', 'playlist', str(uri))
    config.set('CurrentTrack', 'track', str(ttpsreal))
    with open('settings.txt', 'w') as f:
        config.write(f)
    print ("Bye!")
    sys.exit()

if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)

    # Timer function for status update
    # Do we need this?
    # wakeCall = threading.Timer(10, showinfo("self"))
    # Start timer thread
    # wakeCall.start()

    # Setup physical button inputs
	"""
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(17,GPIO.IN)
	GPIO.setup(27,GPIO.IN)
	GPIO.setup(22,GPIO.IN)
	GPIO.setup(9,GPIO.IN)
	GPIO.setup(10,GPIO.IN)
	"""

	# Add interrupts for hardware buttons
	# Doesnt work for now
	#RPIO.add_interrupt_callback(17, gpio_callback, debounce_timeout_ms=100)
	#RPIO.add_interrupt_callback(27, gpio_callback, debounce_timeout_ms=100)
	#RPIO.add_interrupt_callback(22, gpio_callback, debounce_timeout_ms=100)
	#RPIO.add_interrupt_callback(9, gpio_callback, debounce_timeout_ms=100)
	#RPIO.add_interrupt_callback(10, gpio_callback, debounce_timeout_ms=100)
	
	# LCD
	# Configuration parameters
	# I2C Address, Port, Enable pin, RW pin, RS pin, Data 4 pin, Data 5 pin, Data 6 pin, Data 7 pin, Backlight pin (optional)
	lcd = i2c_lcd.i2c_lcd(0x20,1, 2, 1, 0, 4, 5, 6, 7, 3)
	
	# Disable cursor
	lcd.command(lcd.CMD_Display_Control | lcd.OPT_Enable_Display)
	lcd.backLightOn()

	lcd.setPosition(1, 0)
	lcd.writeString("Autospot v0.1")

	print ("Hello")

	try:
		print ("Welcome to Autospot \nCommands:")
		online = internet_on()
		if online == True:
			onlinestatus="online"
		else:
			onlinestatus="offline"
		print ("We are " + onlinestatus)

		logged_in = threading.Event()
		logged_out = threading.Event()
		logged_out.set()
		session = spotify.Session()
		event_loop = spotify.EventLoop(session)
		event_loop.start()
		session.on(
		    spotify.SessionEvent.CONNECTION_STATE_UPDATED,
		    on_connection_state_changed)
		session.on(
		    spotify.SessionEvent.END_OF_TRACK, on_end_of_track)
		session.on(
		    spotify.SessionEvent.LOGGED_IN, on_logged_in)
	  
		# Create audio sink
		print ("Let\'s start by checking your audio subsystem.")
		try:
		    audio_driver = spotify.AlsaSink(session)
		    print ("Audio ok")
		except ImportError:
		    logger.warning(
			'No audio sink found; audio playback unavailable.')

	  

		# Load settings
		global nouri
		nouri=0
		global notrack
		notrack=0
		savedtrack=""
		do_read_settings("dummy")
  
		# See if there are stored values
		if nouri == 1:
		    print ("No playlist saved, we use your latest playlist instead.")
		if notrack == 1:
		    print ("No track saved, we use the first track. ")

		print ("You must be logged in to Spotify")

		if session.remembered_user_name:
			# There is a remembered user
			print ("I remember you!")
			session.relogin()
			#logged_in.wait()
			while session.connection.state is spotify.ConnectionState.LOGGED_OUT:
				pass
			print ("Logged in!")
			print ("Connection state: " + str(session.connection.state))
		else:
			print ("Not logged in")
			# Login
			global username
			global password
			session.login(username, password, remember_me=True)
			logged_in.wait()
			while session.connection.state is spotify.ConnectionState.LOGGED_OUT:
				pass
			print ("Logged in!")
			print ("Logged in as " + session.user_name)
  
		if session.connection.state is spotify.ConnectionState.LOGGED_OUT:
		    print ("Login failed, check your settings")
		    sys.exit()
		# Last played playlist
		print ("Last playlist:" + uri)
		print ("Last track: " + savedtrack)
	  
		# Load all users playlists
		global container
		global cloaded
		do_loaduserspl()

		cloaded = 0

		print ("You have " + str(len(container)) + " playlists.")
		print ("Container:" + str(container[1]))

		pl = str(container[1]).split("'")

		if nouri == 1:
		    print ("nouri=1")
		    print ("First pl is: " + pl[1])
		    # No playlist saved - use users first playlist
		    uri = pl[1]

		print (uri)
		#print str(pl[1])
		# Find index of current playlist
		c = 0
		try:
			while uri != str(pl[1]):
				#print str(c) + "-" + uri + "-" + str(pl[1])
				pl = str(container[c]).split("'")
				c += 1
				#print str(c)
		except:
			print ("Error - last playlist not found")
		#sys.exit()
		# Adjust count
		c -= 1
		#print "Last playlist index is : " + str(c)
		global playlistindex
		playlistindex = c

		# Load last playlist
		global playlist
		playlist = session.get_playlist(uri)
		curplaylist = unicodedata.normalize('NFKD', playlist.name).encode('ascii', 'ignore')

		# Available offline?
		offline = playlist.offline_status
		ofstat = ""
		if offline == 1:
		    ofstat = "*"

		cpl =  curplaylist.decode("utf-8")
		#print ("Last playlist name: " + curplaylist + ofstat + " (\'*\' means available offline)")
		print ("Last playlist name: " + cpl + " (\'*\' means available offline)")

		playlist.load().name
		while not (playlist.is_loaded):
		    pass
	      
		print ("Rpi is " + str(onlinestatus))

		#print str(uri) + " is loaded"

		#print "Playlist loaded (" + str(playlist) + ")"

		"""
		offline = playlist.offline_status
	    
		    if offline == 0:
		      print "Not available offline"
		    if offline == 1:
		      print "Available offline"
		    if offline == 2:
		      print "Download in progress"
		    if offline == 3:
		      print "Waiting for download"
		"""

		#print playlist.tracks

		# Count tracks
		cplaylist = str(playlist.tracks).split(",")
		global nooftracks
		nooftracks = str(len(cplaylist))
		print ("There are " + nooftracks + " tracks in this playlist.")
		# Adjust nooftracks. trackindex starts at 0, nooftracks from 1.

		inooftracks = int(nooftracks)
		inooftracks -= 1
		nooftracks = inooftracks

		# Find track number in playlist

		track = str(cplaylist[1]).split("'")
		cmptrack = track[1]
		print ("cmptrack: " + cmptrack)

		#print "Notrack"
		print (notrack)
		if notrack:
		    print ("Notrack")
		    savedtrack = cmptrack

		print ("savedtrack: " + savedtrack)

		c = 0
		try:
			while savedtrack != cmptrack:
				track = str(cplaylist[c]).split("'")
				cmptrack = track[1]
				print (str(c) + "-" + cmptrack)
				c += 1
		except:
			pass
		# Adjust value
		#c -= 1
		#print "Real track index = " + str(c)
		global trackindex
		trackindex = c
	 
		print ("Trackindex: " + str(trackindex))

		ttpsreal = savedtrack

		print ("All ok - lets play!")
		
		# Use curses to be able ro detect key press
		#init the curses screen
		#stdscr = curses.initscr()
		#use cbreak to not require a return key press
		#curses.cbreak()

		#stdscr.addstr("q-quit\nn-next track\np-prev track\nq-prevpl\nw-nextpl\no-offline\n")
		#stdscr.addstr("Track:"+ str(ttpsreal) + "\n")
		#stdscr.addstr("Trackindex: " + str(trackindex))

		# Check physical buttons
		#RPIO.wait_for_interrupts(threaded=True)

		# Start playback
		#stdscr.addstr("Start play\n")
		#do_play(stdscr)
		do_play()

		# Loop forever
		quit=False
		while quit !=True:
			time.sleep(0.1)
			#cleanexit(stdscr) 
		cleanexit() 
		
	except KeyboardInterrupt:
		cleanexit()
