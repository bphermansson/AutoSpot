#!/usr/bin/env python

from __future__ import unicode_literals
import cmd
import logging
import threading
import sys
import unicodedata
import datetime
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
    # doc_header = 'Commands'
    # prompt = 'spotify> '
    # logger = logging.getLogger('shell.commander')

    def __init__(self):
        print "Welcome to Autospot \nCommands:"
        print "next - Next track"
        print "prev - Previous track"
        print "nextpl - Next playlist"
        print "prevpl - Previous track"
        print "set_offline - Make current playlist available offline"
        print "offstatus - Check offline status for current playlist\n"

        print "Let\'s start by checking your audio subsystem."
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
        global nouri
        global notrack
        global savedtrack
        nouri = 0
        notrack = 0
        self.do_read_settings("dummy")
        if nouri == 1:
            print "No playlist saved, we use your latest playlist instead."
        if notrack == 1:
            print "No track saved, we use the first track. "

        print "You must be logged in to Spotify"

        if self.session.remembered_user_name:
            # There are a remembered user
            self.session.relogin()
            self.logged_in.wait()
        else:
            print "Not logged in"
            # Login
            global username
            global password
            self.session.login(username, password, remember_me=True)
            self.logged_in.wait()
            while self.session.connection.state is spotify.ConnectionState.LOGGED_OUT:
                pass
            print "Logged in!"

        print "Logged in as " + self.session.user_name

        # Logged in?
        # if self.session.connection.state is spotify.ConnectionState.LOGGED_IN:
        #	print "Logged in"
        #else :

        if self.session.connection.state is spotify.ConnectionState.LOGGED_OUT:
            print "Login failed"
            sys.exit()
        # Last played playlist
        global uri
        #print "Last playlist:" + uri
        #print "Last track: " + savedtrack

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

        cloaded = 0
        # Wait until playlists has loaded
        while True:
            if cloaded == 1:
                # print "Playlists loaded"
                break

        print "You have " + str(len(container)) + " playlists."

        #print "Container:" + str(container[1])

        pl = str(container[1]).split("'")

        if nouri == 1:
            #print "First pl is: " + pl[1]
            # No playlist saved - use users first playlist
            uri = pl[1]

        # Find index of current playlist
        c = 0
        try:
            while uri != str(pl[1]):
                #print str(c) + "-" + uri + "-" + str(pl[1])
                pl = str(container[c]).split("'")
                c += 1
            #print str(c)
        except:
            print "Error - last playlist not found"
            sys.exit()
        # Adjust count
        c -= 1
        #print "Last playlist index is : " + str(c)
        global playlistindex
        playlistindex = c

        # Load last playlist
        global playlist
        playlist = self.session.get_playlist(uri)
        curplaylist = unicodedata.normalize('NFKD', playlist.name).encode('ascii', 'ignore')

        # Available offline?
        offline = playlist.offline_status
        ofstat = ""
        if offline == 1:
            ofstat = "*"

        print "Last playlist name: " + curplaylist + ofstat + " (\'*\' means available offline)"

        playlist.load().name
        while not (playlist.is_loaded):
            pass

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
        print "There are " + nooftracks + " tracks in this playlist."
        # Adjust nooftracks. trackindex starts at 0, nooftracks from 1.

        inooftracks = int(nooftracks)
        inooftracks -= 1
        nooftracks = inooftracks

        # Find track number in playlist

        track = str(cplaylist[1]).split("'")
        cmptrack = track[1]
        #print cmptrack


        if notrack:
            savedtrack = cmptrack

        #print "savedtrack: " + savedtrack

        c = 0
        try:
            while savedtrack != cmptrack:
                track = str(cplaylist[c]).split("'")
                cmptrack = track[1]
                #print str(c) + "-" + cmptrack
                c += 1
        except:
            pass
        # Adjust value
        c -= 1
        #print "Real track index = " + str(c)
        global trackindex
        trackindex = c

        #print "Trackindex: " + str(trackindex)

        global ttpsreal
        ttpsreal = savedtrack

        print "All ok - lets play!"

        self.do_play()

    def do_set_offline(self, list):
        "Set playlist offline"
        global playlist
        print "Pl to set offline: " + str(playlist)
        print "Offline: " + str(playlist.offline_status)
        if playlist.offline_status == 0:
            print "Ok, downloading"
            playlist.set_offline_mode(offline=True)
        else:
            print "Removed from harddisk"
            playlist.set_offline_mode(offline=False)

    def do_offstatus(self, list):
        "Offline status"
        print "Downloaded: " + str(playlist.offline_download_completed) + "%"

        offline = playlist.offline_status
        print offline
        if offline == 0:
            print "Not available offline"
        if offline == 1:
            print "Available offline"
        if offline == 2:
            print "Download in progress"
        if offline == 3:
            print "Waiting for download"

    def do_nextpl(self, list):
        "Next playlist"
        global playlistindex
        global container
        global playlist
        # print "Current playlistindex: " + str(playlistindex)
        playlistindex += 1

        pl = str(container[playlistindex]).split("'")
        #print "Next pl is: (" + str(playlistindex) + ") - " + pl[1]

        playlist = self.session.get_playlist(pl[1])
        curplaylist = unicodedata.normalize('NFKD', playlist.name).encode('ascii', 'ignore')

        # Available offline?
        offline = playlist.offline_status
        ofstat = ""
        if offline == 1:
            ofstat = "*"

        print "Playlist name: " + curplaylist + ofstat

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
        self.do_play()


    def do_prevpl(self, list):
        "Previous playlist"
        global playlistindex
        global playlist
        # print "Current playlistindex: " + str(playlistindex)
        playlistindex -= 1

        pl = str(container[playlistindex]).split("'")
        #print "Prev pl is: " + pl[1]

        playlist = self.session.get_playlist(pl[1])
        curplaylist = unicodedata.normalize('NFKD', playlist.name).encode('ascii', 'ignore')

        # Available offline?
        offline = playlist.offline_status
        ofstat = ""
        if offline == 1:
            ofstat = "*"

        print "Playlist name: " + curplaylist + ofstat

        # Find first track in new playlist
        playlist.load().name
        while not (playlist.is_loaded):
            pass
        print "Playlist loaded"

        # Get first track of new playl
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
        #print "In prevpl: uri=" + uri
        #uri = playlist
        # ... and play it
        self.do_play()

    def do_play(self):
        global ttpsreal
        # print "ttpsreal: " + str(ttpsreal)
        track = self.session.get_track(ttpsreal)

        #curartist = unicodedata.normalize('NFKD', track.artists).encode('ascii','ignore')
        curartist = str(track.artists).split("'")
        curartistreal = curartist[1]
        #print "curartistreal: " + curartistreal
        artist = self.session.get_artist(curartistreal)

        curtrack = unicodedata.normalize('NFKD', track.name).encode('ascii', 'ignore')
        print "Now playing: " + artist.load().name + " - " + curtrack
        track.load().name
        self.session.player.load(track)
        while not (track.is_loaded):
            pass
        #print "Track loaded"

        self.session.player.play()

        # Get & print track duration
        dur = track.duration
        d = datetime.timedelta(milliseconds=dur)
        strd = str(d)
        strdm = strd.split(":", 1)
        #print "Duration: " + str(dur)
        print "Track length: " + str(strdm[1])

    # Move to end to test next track functions
    # seekto = dur - 5000
    #self.session.player.seek(seekto)

    def do_read_settings(self, line):

        # Load & read configuration
        # Settings are stored in a file called "settings".
        # Example:
        # [Spotify]
        # username=<Spotify username>
        # pass=<Spotify password>

        print "Load"
        config = ConfigParser.ConfigParser()
        try:
            print "Load settings!"
            config.read("settings.txt")
        except:
            print "Settings file not found"
            sys.exit()
        print config.sections()

        try:
            options = config.options("Spotify")
            global username
            try:
                username = config.get("Spotify", "username")
            except:
                print "No username given"
            global password
            password = config.get("Spotify", "pass")
            print "Credentials: " + username + ":" + password
            global autoplay
            try:
                autoplay = config.get("General", "autoplay")
                print "Autoplay: " + autoplay
            except:
                print "No autoplay setting found"
            global uri
            global savedtrack
            global playlistnr

            try:
                uri = config.get("CurrentTrack", "playlist")
            except:
                print "No uri saved"
                global nouri
                nouri = 1
                #uri = "spotify:user:phermansson:playlist:7JaJFymSwbFcceatOd40Af"
            try:
                savedtrack = config.get("CurrentTrack", "track")
            except:
                print "No track saved"
                global notrack
                notrack = 1
            #savedtrack = "spotify:track:583jvp9iPtaOphRa74h0A8"

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
        # while not (container.is_loaded):
        #	pass
        #print "Playlists loaded"
        #print container.is_loaded
        temp = container.load()

    def on_connection_state_changed(self, session):
        if session.connection.state is spotify.ConnectionState.LOGGED_IN:
            self.logged_in.set()
            self.logged_out.clear()
        elif session.connection.state is spotify.ConnectionState.LOGGED_OUT:
            self.logged_in.clear()
        self.logged_out.set()

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

    def on_container_loaded(self, session):
        global cloaded
        #print "Container loaded"
        cloaded = 1

    def on_end_of_track(self, session):
        # global trackindex
        # global tracks
        # global nooftracks

        print "End of track"
        self.do_next(self)

    def on_logged_in(self, session, dummy):
        pass


    def do_next(self, line):
        "Next track"
        global trackindex
        global playlist
        global ttpsreal
        global nooftracks
        global uri
        print "uri=" + str(uri)

        # Check if at end of playlist
        if trackindex < nooftracks:
            print "Next track"
            trackindex += 1
            print "Trackindex: " + str(trackindex)
            self.playnext()

        else:
            print "End of playlist"
            # Stop playback
            self.session.player.play(False)
            trackindex = 0
            self.playnext()


    def do_prev(self, line):
        "Previous track"
        global trackindex
        global playlist
        global ttpsreal
        global nooftracks

        # Check if at end of playlist
        if trackindex > 0:
            print "Next track"
            trackindex -= 1
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




#print "We received a 'on_logged_in'"
def showinfo(list):
    print "Time!"


if __name__ == '__main__':
    #logging.basicConfig(level=logging.INFO)
    logging.basicConfig(level=logging.INFO)

    # Timer function for status update
    # Do we need this?
    # wakeCall = threading.Timer(10, showinfo("self"))
    # Start timer thread
    # wakeCall.start()

    print "Hello"

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
        config.read('settings.txt')
        # Is there a CurrentTrack section already?
        try:
            config.add_section('CurrentTrack')
        except:
            pass
        config.set('CurrentTrack', 'playlist', str(uri))
        config.set('CurrentTrack', 'track', str(ttpsreal))
        #config.set('CurrentTrack', 'trackindex',  str(trackindex))

        with open('settings.txt', 'w') as f:
            config.write(f)

        print "Bye!"
        sys.exit()