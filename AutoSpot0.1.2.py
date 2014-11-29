#!/usr/bin/env python
 
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
global cleantrack, trackindex, tracks
global username, password, autoplay
global curtrack
global selPlaylist
global nooftracks
selPlaylist = 0

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
			print "Audio ok" 
		except ImportError:
			self.logger.warning(
			'No audio sink found; audio playback unavailable.')

		# Load settings
		self.do_read_settings("dummy")

		# Logged in?
		if self.session.connection.state is spotify.ConnectionState.LOGGED_IN:
			print "Logged in"
		else :
			print "Not logged in"	
			# Login		
			global username
			global password
			self.session.login(username, password, remember_me=True)
			self.logged_in.wait()
			while self.session.connection.state is spotify.ConnectionState.LOGGED_OUT:
				pass
			print "Logged in!"
		
		if self.session.connection.state is spotify.ConnectionState.LOGGED_OUT:
			print "Login failed"
		
		# Last played playlist
		global uri
		print "Last playlist:" + uri
		print "Last track: " + savedtrack
		
		pl = self.session.playlist_container
		pl.load()
		#print "pl:" + str(pl)
		
		# Trigger for playlists loaded event
		# What to do when playlists are loaded? 
		pl.on(
			spotify.PlaylistContainerEvent.CONTAINER_LOADED, self.on_container_loaded)

		
		# Load all users playlists
		global container
		global cloaded
		self.do_loaduserspl(self)
		
		cloaded=0
		# Wait until playlists has loaded
		# This never triggers?
		#while True:
		#	if cloaded == 1:
		#		print "Break"
		#		break
		
		print "There are " + str(len(container)) + " playlists."	

		print "Container:" + str(container[1])
		
		pl = str(container[1]).split("'")
		#print "First pl is: " + pl[1]
		
		# Find index of current playlist
		c=0
		try: 
			while uri != str(pl[1]):
				#print str(c) + "-" + uri + "-" + str(pl[1])
				pl = str(container[c]).split("'")
				c+=1
				#print str(c)
		except:
			print "Error - last playlist not found"
			self.system.exit()
		# Adjust count
		c-=1
		print "Last playlist index is : " + str(c)
		global playlistindex
		playlistindex = c
		
		# Load last playlist
		global playlist
		playlist = self.session.get_playlist(uri)
		curplaylist =  unicodedata.normalize('NFKD', playlist.name).encode('ascii','ignore')	
		print "Playlist name: " + curplaylist
		playlist.load().name
		while not (playlist.is_loaded):
			pass
		#print "Playlist loaded (" + str(playlist) + ")" 
		
		offline = playlist.offline_status
		
		if offline == 0:
			print "Not available offline"
		if offline == 1:
			print "Available offline"
		if offline == 2:
			print "Download in progress"
		if offline == 3:
			print "Waiting for download"
				
		#print "Offline: " + str(playlist.offline_status)
		
		
		#print playlist.tracks
		
		# Count tracks
		cplaylist = str(playlist.tracks).split(",")
		global nooftracks
		nooftracks = str(len(cplaylist))
		print "There are " + nooftracks + " tracks."	
		# Adjust nooftracks. trackindex starts at 0, nooftracks from 1.
		
		inooftracks = int(nooftracks) 
		inooftracks -=1
		nooftracks = inooftracks
		
		# Find track number in playlist
		
		track = str(cplaylist[1]).split("'")
		cmptrack = track[1]
		#print cmptrack
		
		print "savedtrack: " + savedtrack
		
		c=0
		try: 
			while savedtrack != cmptrack:
				track = str(cplaylist[c]).split("'")
				cmptrack = track[1]
				print cmptrack
				c+=1
		except:
			pass
		# Adjust value
		c-=1
		print "Real track index = " + str(c)
		global trackindex
		trackindex=c
		
		print "Trackindex: " + str(trackindex)
		
		global ttpsreal
		ttpsreal = savedtrack
		self.do_play()
		
	def do_set_offline(self, list):
		global playlist
		print "Pl to set offline: " + str(playlist)
		print "Offline: " + str(playlist.offline_status)
		playlist.set_offline_mode(offline=True)
		
		
	def do_offstatus(self,list):
		 print "Downloaded: " + str(playlist.offline_download_completed) + "%"

	def do_nextpl(self, list):
		global playlistindex
		global container
		print "Current playlistindex: " + str(playlistindex)
		playlistindex+=1
		
		pl = str(container[playlistindex]).split("'")
		print "Next pl is: (" + str(playlistindex) + ") - " + pl[1]
		
		playlist = self.session.get_playlist(pl[1])
		curplaylist =  unicodedata.normalize('NFKD', playlist.name).encode('ascii','ignore')	
		print "Playlist name: " + curplaylist
		
		# Find first track in new playlist
		playlist.load().name
		while not (playlist.is_loaded):
			pass
		print "Playlist loaded"
		
		# Get first track of new playl
		print str(playlist.tracks[0])
		firsttrack = str(playlist.tracks[0])
		firsttrackar = firsttrack.split("'")
		print "First track of new list: " + firsttrackar[1]
		global ttpsreal
		ttpsreal = firsttrackar[1]
		global trackindex
		trackindex=0
		global uri
		realuri = str(playlist)
		ruri = realuri.split("'")
		uri = ruri[1]
		print "In nextpl: uri=" + uri
		#uri = playlist
		# ... and play it
		self.do_play()


	def do_prevpl(self, list):
		global playlistindex
		print "Current playlistindex: " + str(playlistindex)
		playlistindex-=1
		
		pl = str(container[playlistindex]).split("'")
		print "Prev pl is: " + pl[1]
		
		playlist = self.session.get_playlist(pl[1])
		curplaylist =  unicodedata.normalize('NFKD', playlist.name).encode('ascii','ignore')	
		print "Playlist name: " + curplaylist
		
		# Find first track in new playlist
		playlist.load().name
		while not (playlist.is_loaded):
			pass
		print "Playlist loaded"
		
		# Get first track of new playl
		print str(playlist.tracks[0])
		firsttrack = str(playlist.tracks[0])
		firsttrackar = firsttrack.split("'")
		print "First track of new list: " + firsttrackar[1]
		global ttpsreal
		ttpsreal = firsttrackar[1]
		global trackindex
		trackindex=0
		global uri
		realuri = str(playlist)
		ruri = realuri.split("'")
		uri = ruri[1]
		print "In prevpl: uri=" + uri
		#uri = playlist
		# ... and play it
		self.do_play()
		
	def do_play(self):
		global ttpsreal
		print "ttpsreal: " + str(ttpsreal) 
		track = self.session.get_track(ttpsreal)
		
		#curartist = unicodedata.normalize('NFKD', track.artists).encode('ascii','ignore')	
		curartist = str(track.artists).split("'")
		curartistreal = curartist[1]
		#print "curartistreal: " + curartistreal
		artist = self.session.get_artist(curartistreal)
		
		curtrack =  unicodedata.normalize('NFKD', track.name).encode('ascii','ignore')	
		print artist.load().name + " - " + curtrack
		track.load().name
		self.session.player.load(track)
		while not (track.is_loaded):
			pass
		print "Track loaded"
		
		self.session.player.play()

		dur = track.duration
		print "Duration: " + str(dur)

		# Move to end to test next track functions
		#seekto = dur - 5000
		#self.session.player.seek(seekto)
		
	def do_read_settings(self,line):
		
		# Load & read configuration
		# Settings are stored in a file called "settings".
		# Example:
		#[Spotify]
		#username=<Spotify username>
		#pass=<Spotify password>

		Config = ConfigParser.ConfigParser()
		try: 
			print "Load settings"
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
			global savedtrack
			global playlistnr
			
			try: 
				uri = Config.get("CurrentTrack", "playlist")
			except: 
				print "No uri saved"
				uri = "spotify:user:phermansson:playlist:7JaJFymSwbFcceatOd40Af"
			try:
				savedtrack = Config.get("CurrentTrack", "track")
			except:
				print "No track saved"
				savedtrack = "spotify:track:583jvp9iPtaOphRa74h0A8"
				
			#global trackindex
			#trackindex = int(Config.get("CurrentTrack", "trackindex"))
			#try: 
			#	playlistnr = int(Config.get("playlist", "playlistnr"))
			#except:
			#	"No playlistnumbed saved"
			#	playlistnr = 0
		except: 
			print "Error reading settings"
			sys.exit(0)

	def do_loaduserspl(self, line):
		print "Load users playlists"
		global container
		container = self.session.playlist_container
		#while not (container.is_loaded):
		#	pass
		#print "Playlists loaded"
		#print container.is_loaded
		temp = container.load()
		#print container.is_loaded
		
		print "Loaded pls"
		
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
	def on_container_loaded(self, session):
		global cloaded
		print "Container loaded"
		cloaded = 1
	def on_connection_state_changed(self, session):
		if session.connection.state is spotify.ConnectionState.LOGGED_IN:
			self.logged_in.set()
			self.logged_out.clear()
		elif session.connection.state is spotify.ConnectionState.LOGGED_OUT:
			self.logged_in.clear()
		self.logged_out.set()
	def on_end_of_track(self, session):
		#global trackindex
		#global tracks
		#global nooftracks
		
		print "End of track"
		self.do_next(self)
		
	def do_next(self,line):
		global trackindex
		global playlist		
		global ttpsreal
		global nooftracks
		
		# Check if at end of playlist
		if trackindex < nooftracks:
			print "Next track"
			trackindex+=1
			print "Trackindex: " + str(trackindex)
			self.playnext()
		
		else:
			print "End of playlist"
			# Stop playback
			self.session.player.play(False)
			trackindex = 0
			self.playnext()
	def do_prev(self,line):
		global trackindex
		global playlist		
		global ttpsreal
		global nooftracks
		
		# Check if at end of playlist
		if trackindex > 0:
			print "Next track"
			trackindex-=1
			print "Trackindex: " + str(trackindex)
			self.playnext()
		
		else:
			print "Beginning of playlist"
			# Stop playback
			self.session.player.play(False)
			trackindex = 0
			self.playnext()
				
	def playnext(self):
		global trackindex
		global ttpsreal
		global playlist
		print trackindex
		ttp = str(playlist.tracks[trackindex])
		ttps = ttp.split("'")
		ttpsreal = ttps[1]
		print "Track to play: " + str(ttpsreal)
		uri = str(ttpsreal)
		self.do_play()
			
	def on_logged_in(self, session, dummy):
		print "We received a 'on_logged_in'"
	
		
if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)
	try: 
		Commander().cmdloop()
	except KeyboardInterrupt:
		global uri, ttpsreal, trackindex
		print "Current playlist " + str(uri) 
		print "Current track: " + str(ttpsreal)
		#print "Track index: " + str(trackindex)
		
		#session.player.stop()

		
		# Save info
		from ConfigParser import SafeConfigParser
		config = SafeConfigParser()
		config.read('settings')
		# Is there a CurrentTrack section already?
		try: 
			config.add_section('CurrentTrack')
		except: 
			pass
		config.set('CurrentTrack', 'playlist',  str(uri))	
		config.set('CurrentTrack', 'track',  str(ttpsreal))
		#config.set('CurrentTrack', 'trackindex',  str(trackindex))		
	
		with open('settings', 'w') as f:
			config.write(f)
		
		
		print "Bye!"
		sys.exit()