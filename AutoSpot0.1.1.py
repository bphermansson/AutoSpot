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
		print "Last playlist:" + uri
		print "Last track: " + savedtrack
		
		# Load last playlist
		playlist = self.session.get_playlist(uri)
		curplaylist =  unicodedata.normalize('NFKD', playlist.name).encode('ascii','ignore')	
		print "Playlist name: " + curplaylist
		playlist.load().name
		while not (playlist.is_loaded):
			pass
		print "Playlist loaded"
		
		print playlist.tracks
		
		print "Trackindex: " + str(trackindex)
		ttp = str(playlist.tracks[trackindex])
		ttps = ttp.split("'")
		ttpsreal = ttps[1]
		print "Track to play: " + str(ttpsreal)
		
		track = self.session.get_track(ttpsreal)
		
		#track = self.session.get_track(savedtrack)
		curtrack =  unicodedata.normalize('NFKD', track.name).encode('ascii','ignore')	
		print "Track name: " + curtrack
		track.load().name
		while not (track.is_loaded):
			pass
		print "Track loaded"
		""
		
		# Load playlists
		#self.do_loaduserspl(username)
		
		#print container[0]

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
			uri = Config.get("playlist", "uri")
			global savedtrack
			savedtrack = Config.get("CurrentTrack", "track")
			global trackindex
			trackindex = int(Config.get("CurrentTrack", "trackindex"))
			global playlistnr
			playlistnr = int(Config.get("playlist", "playlistnr"))
		except: 
			print "Error reading settings"
			sys.exit(0)

	def do_loaduserspl(self, line):
		print "Load users playlists"
		global container
		container = self.session.playlist_container
		while not (container.is_loaded):
			pass
		print "Playlists loaded"
		container.load()
		print "There are " + str(len(container)) + " playlists."	
		
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
	def on_connection_state_changed(self, session):
		if session.connection.state is spotify.ConnectionState.LOGGED_IN:
			self.logged_in.set()
			self.logged_out.clear()
		elif session.connection.state is spotify.ConnectionState.LOGGED_OUT:
			self.logged_in.clear()
		self.logged_out.set()
	def on_end_of_track(self, session):
		global trackindex
		global items 
		global tracks
		print "End of track"
		# Stop playback
		self.session.player.play(False)
	def on_logged_in(self, session, dummy):
		print "We received a 'on_logged_in'"
	
		
if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)
	try: 
		Commander().cmdloop()
	except KeyboardInterrupt:
		print "Bye!"
		sys.exit()