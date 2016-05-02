#!/usr/bin/env python

# How simple can a Spotify player be?

import sys
import threading
import spotify
# Import file with settings (settings.py):
import settings

def on_connection_state_changed(session):
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()
        logged_out.clear()
    elif session.connection.state is spotify.ConnectionState.LOGGED_OUT:
        logged_in.clear()
        logged_out.set()

def do_logout(line):
        "logout"
        session.logout()
        logged_out.wait()
        
track_uri = 'spotify:track:6xZtSE6xaBxmRozKA0F6TA'

session = spotify.Session()

session.on(
    spotify.SessionEvent.CONNECTION_STATE_UPDATED,
    on_connection_state_changed)

loop = spotify.EventLoop(session)
loop.start()

audio = spotify.AlsaSink(session)

logged_in = threading.Event()


try:
        username = settings.username
        password = settings.password
        print "User credentials from settings file: " + username + "-" + password
except: 
        print "No username or password given"
        sys.exit(0)

remUser = session.remembered_user_name
print "Remembered user: " + str(remUser)
if not remUser:
      print "Wait for login " + username 
      session.login(username, password, remember_me=True)
      logged_in.wait()
else:
      session.relogin()	# Spotify remembers us, just relogin
      logged_in.wait()



track = session.get_track(track_uri).load()
session.player.load(track)
session.player.play()
