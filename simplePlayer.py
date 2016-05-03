#!/usr/bin/env python

"""
This is an example of playing music from Spotify using pyspotify.
https://raw.githubusercontent.com/mopidy/pyspotify/v2.x/develop/examples/play_track.py

The example use the :class:`spotify.AlsaSink`, and will thus only work on
systems with an ALSA sound subsystem, which means most Linux systems.

You can either run this file directly without arguments to play a default
track::

    python play_track.py

Or, give the script a Spotify track URI to play::

    python play_track.py spotify:track:3iFjScPoAC21CT5cbAFZ7b
"""

from __future__ import unicode_literals

import sys
import threading
import spotify

# Import file with settings (settings.py):
import settings

if sys.argv[1:]:
    track_uri = sys.argv[1]
else:
    track_uri = 'spotify:track:6xZtSE6xaBxmRozKA0F6TA'

# Assuming a spotify_appkey.key in the current dir
session = spotify.Session()

# Process events in the background
loop = spotify.EventLoop(session)
loop.start()

# Connect an audio sink
audio = spotify.AlsaSink(session)

# Events for coordination
logged_in = threading.Event()
end_of_track = threading.Event()


def on_connection_state_updated(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()


def on_end_of_track(self):
    end_of_track.set()


# Register event listeners
session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, on_connection_state_updated)
session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)

# Login
try:
    username = settings.username
    password = settings.password
    print "User credentials from settings file: " + username + "-" + password
except: 
    print "No username or password given in settings.py"
    sys.exit(0)

try:
    session.relogin()
    logged_in.wait()

except:
    print "No previous login"
    session.login(username, password, remember_me=True)
    logged_in.wait()

# Play a track
track = session.get_track(track_uri).load(timeout=60)
session.player.load(track)
session.player.play()

# Wait for playback to complete or Ctrl+C
try:
    while not end_of_track.wait(0.1):
        pass
except KeyboardInterrupt:
    pass
