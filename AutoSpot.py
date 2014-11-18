#!/usr/bin/env python

"""
Raspo
Patrik Hermansson 2014

Based on "shell.py" from Pyspotify examples, https://pyspotify.mopidy.com/en/latest/

TODO:
Store playlist, current track and position at KeyboardInterrupt/Exit
Load  the same at start
Function for next/prev playlist


-------------
This is an example of a simple command line client for Spotify using pyspotify.

You can run this file directly::

    python shell.py

Then run the ``help`` command on the ``spotify>`` prompt to view all available
commands.
"""

from __future__ import unicode_literals

import cmd
import logging
import threading
import sys
import unicodedata

import spotify

# To load config file
import ConfigParser

global curplaylist
global playlist
global cleantrack
global username, password, autoplay
global selPlaylist
selPlaylist = 0

# Load & read configuration
# Settings are stored in a file called "settings".
# Example:
#[Spotify]
#username=<Spotify username>
#pass=<Spotify password>

Config = ConfigParser.ConfigParser()
try: 
	Config.read("settings")
except: 
	print "Settings file not found"
#print Config.sections()
try: 
	options = Config.options("Spotify")
	global username 
	username = Config.get("Spotify", "username")
	global password 
	password = Config.get("Spotify", "pass")
	print "Credentials: "+ username + ":" + password 
	global autoplay
	autoplay = Config.get("General", "autoplay")
	print "Autoplay: " + autoplay
	global uri
	uri = Config.get("playlist", "uri")
	
except: 
	print "Error reading settings"
	sys.exit(0)

class Commander(cmd.Cmd):

    doc_header = 'Commands'
    prompt = 'spotify> '

    logger = logging.getLogger('shell.commander')

    def __init__(self):
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

	# Create audio sink
        try:
            self.audio_driver = spotify.AlsaSink(self.session)
        except ImportError:
            self.logger.warning(
                'No audio sink found; audio playback unavailable.')

	# Logged in?
	if self.session.connection.state is spotify.ConnectionState.LOGGED_IN:
		print "Logged in"
	else :
		print "Not logged in"		
		#self.session.login('phermansson', 'MciaS96DL1962', remember_me=True)
		global username
		global password
		self.session.login(username, password, remember_me=True)

		#self.logged_in.wait()
		#while self.session.connection.state is spotify.ConnectionState.LOGGED_OUT:
		#	dummy=0
		#print "Logged in!"
		
	# Get user playlists
	username = self.session.user_name
	print "Current user: " + username
	
	# Get user playlists
	pl = self.session.playlist_container
	#print "pl:" + str(pl)
	plstone = pl[2]
	#print "Playlist:"
	plstonestr = str(plstone)
	#print plstonestr
	self.plist = plstonestr.split('\'') 
	#print "plist[1]: " + self.plist[1]
	
	# Browse through users playlists
	c=0
	usersplaylists = []
	usersplaylists.append([])
	usersplaylists.append([])
	usersplaylists.append([])
	
	for item in pl:
		#print str(c) + " - " + str(item)
		item=str(item)
		playlisturi = item.split("'")
		# Get real names for playlists, except for playlist group names
		try: 
			playlistname = self.session.get_playlist(playlisturi[1])
			playlistname=playlistname.name
			playlistname =  unicodedata.normalize('NFKD', playlistname).encode('ascii','ignore')	
			#print str(c) + " - " + playlistname
			# Save info
			global usersplaylists
			usersplaylists[0].append(str(c))
			usersplaylists[1].append(playlistname)
			usersplaylists[2].append(str(playlisturi[1]))			
		except:
			pass
		c+=1

	print ("We find %i playlists",c)
	
	for x in range(0, 10):
		print usersplaylists[0][x] + "-" + usersplaylists[1][x] 
	
	#print "Plist1: " + self.plist[1]
	
	if autoplay == "y":
		print "Autoplay on"
		print "Uri: " + uri
	
	playlist = self.session.get_playlist(uri)
	
	#playlist = self.session.get_playlist(self.plist[1])
	#playlist.load().name
	curplaylist = playlist.name
	
	# Convert unicode to printable data
	curplaylist =  unicodedata.normalize('NFKD', curplaylist).encode('ascii','ignore')	
	playlistname = curplaylist.encode('utf-8')
	print "Playlist Name: " + playlistname
	
	alltracks = str(playlist.tracks)
	#print "alltracks:\n " + alltracks
	tracks = alltracks.split(",")
	cleantracks = tracks[0].split("'")
	global cleantrack
	cleantrack = cleantracks[1]
	#print "Cleantrack:" + cleantrack
	
	track = self.session.get_track(cleantrack)
	track.load()
	
	# Now playing
	artists = str(track.artists)
	#print "Artists: " + artists
	artists = artists.split("'")
	#print artists[1]
	realartist = self.session.get_artist(artists[1])
	print "Realartist: " + str(realartist.name)
	# artist.load().name
	
	#print "Artist: " + artists
	realtrack =  unicodedata.normalize('NFKD', track.name).encode('ascii','ignore')	

	#realtrack = str(track.name)
	print "Track: " + realtrack
	
	self.logger.info('Loading track into player')
        self.session.player.load(track)
        self.logger.info('Playing track')
        self.session.player.play()
	
	
    def do_loadpl(self, list):
	"loadpl <pnr>"
	print "Loading playlist #" + list
	print "Nr: " + usersplaylists[0][int(list)]
	print "Name: " + usersplaylists[1][int(list)]
	print "Uri: " + usersplaylists[2][int(list)]	
	uri = usersplaylists[2][int(list)]
	
	playlist = self.session.get_playlist(uri)
	# Get tracks in playlist
	alltracks = str(playlist.tracks)
	#print "alltracks:\n " + alltracks
	#Get track #1
	tracks = alltracks.split(",")
	cleantracks = tracks[0].split("'")
	global cleantrack
	cleantrack = cleantracks[1]
	#print "Cleantrack, track #1:" + cleantrack
	
	# Load track
	track = self.session.get_track(cleantrack)
	track.load()
	
	# Now playing
	artists = str(track.artists)
	#print "Artists: " + artists
	artists = artists.split("'")
	#print artists[1]
	realartist = self.session.get_artist(artists[1])
	print "Realartist: " + str(realartist.name)
	
	#print "Artist: " + artists
	realtrack =  unicodedata.normalize('NFKD', track.name).encode('ascii','ignore')	

	#realtrack = str(track.name)
	print "Track: " + realtrack
	
	self.logger.info('Loading track into player')
        self.session.player.load(track)
        self.logger.info('Playing track')
        self.session.player.play()
	
	# Save current playlist
	from ConfigParser import SafeConfigParser
	config = SafeConfigParser()
	config.read('settings')
	# Is there a x section already?
	try: 
		config.add_section('playlist')
	except: 
		pass
	config.set('playlist', 'artist',  str(realartist.name))
	config.set('playlist', 'playlistname', usersplaylists[1][int(list)])
	config.set('playlist', 'uri', uri)

	with open('settings', 'w') as f:
		config.write(f)
	
	
    def do_next_track(self):
	print ("Next track")
	
	
    def on_connection_state_changed(self, session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self.logged_in.set()
            self.logged_out.clear()
        elif session.connection.state is spotify.ConnectionState.LOGGED_OUT:
            self.logged_in.clear()
            self.logged_out.set()

    def on_end_of_track(self, session):
        self.session.player.play(False)
	
    def on_logged_in(self, session, dummy):
	print "on_logged_in"

    def precmd(self, line):
        if line:
            self.logger.debug('New command: %s', line)
        return line

    def emptyline(self):
        pass

    def do_debug(self, line):
        "Show more logging output"
        print('Logging at DEBUG level')
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

    def do_info(self, line):
        "Show normal logging output"
        print('Logging at INFO level')
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

    def do_warning(self, line):
        "Show less logging output"
        print('Logging at WARNING level')
        logger = logging.getLogger()
        logger.setLevel(logging.WARNING)

    def do_EOF(self, line):
        "Exit"
        if self.logged_in.is_set():
            print('Logging out...')
            self.session.logout()
            self.logged_out.wait()
        self.event_loop.stop()
        print('')
        return True

    def do_test(self, line):
        "Do test"
        self.logger.info('I am from %s', self.session.user_country)

    def do_playlists(self, line):
        "Show playlists"
	#Get username
	#print self.session.user
	username = self.session.user_name
	print username
	#self.logger.info('%s', self.session.playlist_container)
	pl = self.session.playlist_container
	plstone = pl[2]
	#self.logger.info('%s', pl[1])
	print "Playlist:"
	plstonestr = str(plstone)
	self.plist = plstonestr.split('\'') 
	print self.plist[1]
	c=0
	for item in pl:
		c+=1
	print ("We find %i playlists",c)
	
	plsttoload = "'spotify:user:" + username + ":playlist:" + str(plstone) + "'"
	print plsttoload
	
	#playlist = self.session.get_playlist('spotify:user:fiat500c:playlist:54k50VZdvtnIPt4d8RBCmZ')
	global playlist
	playlist = self.session.get_playlist(self.plist[1])
	playlist.load().name
	global curplaylist
	curplaylist = playlist.name
	playlistname = curplaylist.encode('utf-8')
	print playlistname
	
    def do_gettrack(self, line):
        "gettrack"
	# Get current playlist
	playlistname = curplaylist.encode('utf-8')
        print playlistname
	playlist.load().name
	alltracks = str(playlist.tracks)
	print alltracks
	tracks = alltracks.split(",")
	cleantracks = tracks[1].split("'")
	global cleantrack
	cleantrack = cleantracks[1]
	print cleantrack
	# Play a track
	#track = session.get_track(cleantrack).load()
	#self.player.load(cleantrack)
	#self.player.play()
	
    def do_play(self, line):
        print "Track to play: "
	print cleantrack
	track = self.session.get_track(cleantrack)
	track.load()
	self.logger.info('Loading track into player')
        self.session.player.load(track)
        self.logger.info('Playing track')
        self.session.player.play()

    def do_login(self, line):
        #"login <username> <password>"
        #username, password = line.split(' ', 1)
        #self.session.login(username, password, remember_me=True)
	"login"
	self.session.login('phermansson', 'MciaS96DL1962', remember_me=True)
        self.logged_in.wait()

    def do_relogin(self, line):
        "relogin -- login as the previous logged in user"
        try:
            self.session.relogin()
            self.logged_in.wait()
        except spotify.Error as e:
            self.logger.error(e)

    def do_forget_me(self, line):
        "forget_me -- forget the previous logged in user"
        self.session.forget_me()

    def do_logout(self, line):
        "logout"
        self.session.logout()
        self.logged_out.wait()

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

    def do_play_uri(self, line):
        "play <spotify track uri>"
        if not self.logged_in.is_set():
            self.logger.warning('You must be logged in to play')
            return
        try:
            track = self.session.get_track(line)
            track.load()
        except (ValueError, spotify.Error) as e:
            self.logger.warning(e)
            return
        self.logger.info('Loading track into player')
        self.session.player.load(track)
        self.logger.info('Playing track')
        self.session.player.play()

    def do_pause(self, line):
        self.logger.info('Pausing track')
        self.session.player.play(False)

    def do_resume(self, line):
        self.logger.info('Resuming track')
        self.session.player.play()

    def do_stop(self, line):
        self.logger.info('Stopping track')
        self.session.player.play(False)
        self.session.player.unload()

    def do_seek(self, seconds):
        "seek <seconds>"
        if not self.logged_in.is_set():
            self.logger.warning('You must be logged in to play')
            return
        # TODO Check if playing
        self.session.player.seek(int(seconds) * 1000)

    def do_search(self, query):
        "search <query>"
        if not self.logged_in.is_set():
            self.logger.warning('You must be logged in to search')
            return
        try:
            result = self.session.search(query)
            result.load()
        except spotify.Error as e:
            self.logger.warning(e)
            return
        self.logger.info(
            '%d tracks, %d albums, %d artists, and %d playlists found.',
            result.track_total, result.album_total,
            result.artist_total, result.playlist_total)
        self.logger.info('Top tracks:')
        for track in result.tracks:
            self.logger.info(
                '[%s] %s - %s', track.link, track.artists[0].name, track.name)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
	
    Commander().cmdloop()
