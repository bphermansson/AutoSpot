#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

# Upload changes to Github:
# git commit -a
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
from Tkinter import *


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
    print "In on_logged_in, Logged in"
    logged_in.set()
    
def on_end_of_track(session):
    print "Track ended"
    nextTrack()

def contLoaded(session, error_type):
    print "Container loaded"
def nextTrack():
    global trackindex
    global nooftracks
    global playlisturis
    print "In nextTrack: Pl has " + str(nooftracks) + " tracks. trackindex = " + str(trackindex)
    inttrack = int(trackindex)
    intnooftracks = int(nooftracks)
    if(inttrack<intnooftracks-1):
        inttrack+=1
        print "Trackindex: " + str(inttrack) + "/" + str(intnooftracks)
        #print playlisturis
        #dur = track.load().duration
        #print str(dur/1000) + " sec"
        trackindex=str(inttrack)
        play(playlisturis[inttrack])
        #time.sleep(2)
        #print session.player.state
    
        # Debug: Jump to end of track to see end of track callback
        #session.player.seek(dur-100)
    else:
        print "End of playlist"
        changePl("next")
        
def prevTrack():
    global trackindex
    global nooftracks
    if(trackindex>=0):
        print "trackindex" + str(trackindex) + "/" + str(nooftracks) 
        print playlisturis[trackindex]
        trackindex-=1
        play(playlisturis[trackindex])
    else:
        print "End of playlist"
        
def changePl(dir):
    print dir
    global playlistnr
    global trackindex
    global nooftracks
    global playlisturis
    global pl
    trackindex = 0
    # Next or previous playlist?
    if(dir=="next"):
        playlistnr+=1
    elif(dir=="prev"):
        playlistnr-=1
    else:
        print "Playlist change error"
    print "Playlist # " +str(playlistnr)
    pl = str(container[playlistnr]).split(":")
    print "New pl = " + str(pl)
    pluser = pl[2]
    pluri = pl[4].split("'")
    pl = pluri[0]
    print "New pl (short)= " + str(pl)

    #print pluser + pluri[0] # == phermansson5Lg5sAr6bKzEYCq8LbewLM
    # Should be like "'spotify:user:fiat500c:playlist:54k50VZdvtnIPt4d8RBCmZ'"
    getpluri = "spotify:user:" + pluser + ":playlist:" + pluri[0]
    #print getpluri
    playlist = session.get_playlist(getpluri)
    #print playlist
    curpl = unicodedata.normalize('NFKD', playlist.load().name).encode('ascii', 'ignore')
    print curpl
    
    # Create a list with the playlists tracks
    nooftracks = len(playlist.tracks)
    print str(nooftracks) + " tracks."
    playlisturis=[]
    for x in range(0, nooftracks):
        curtrack = str(playlist.tracks[x])
        curtrackuri = curtrack.split("'")
        playlisturis.append(curtrackuri[1])
    #print playlisturis[1]
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
    lblOffline["text"]=offline_status

    play(playlisturis[1])

    #session.player.load(track)
    #session.player.play()
    #time.sleep(2)
    #print session.player.state
    
    # Debug: Jump to end of track to see end of track callback
    #session.player.seek(dur-100)

def play(curtrack):
    global trackindex
    global artistname
    global trackname
    global trackofflinestatus, offlinetxt

    print "In play, curtrack=" + str(curtrack)
    track = session.get_track(curtrack).load()
    #print track
    trackname=track.load().name
    
    dur = track.load().duration
    print "Track:" + str(trackindex) + "-" + trackname + " length:" + str(dur)

    # Get artist code
    artist=track.load().artists
    #print artist
    temp = str(artist).split(":")
    #print temp
    art = temp[2].split("'")
    #print art[0]
    artisturi="spotify:artist:" + art[0]
    artist = session.get_artist(artisturi)
    artistname = artist.load().name
    """artist = session.get_artist(
...     'spotify:artist:22xRIphSN7IkPVbErICu7s')
>>> artist.load().name"""
    
    curtrack = unicodedata.normalize('NFKD', trackname).encode('ascii', 'ignore')
    curartist = unicodedata.normalize('NFKD', artistname).encode('ascii', 'ignore')
    trackname = curtrack # Global var for Gui
    print curartist + "-" + curtrack
    session.player.load(track)

    # Track available offline?
    trackofflinestatus = track.offline_status
    if trackofflinestatus == 0:
        offlinetxt="Not available offline"
    if trackofflinestatus == 1:
        offlinetxt = "Available offline"
    if trackofflinestatus == 2:
	    offlinetxt = "Download in progress"
    if trackofflinestatus == 3:
        offlinetxt = "Waiting for download\n"
    print "Offline? " + str(trackofflinestatus) + " - " + offlinetxt


    session.player.play()
    #status["text"]= "Playing"

    # Debug: Jump to end of track to see end of track callback
    #session.player.seek(dur-100)

def playerPause():
    status["text"]="Play/Pause"
    ps=session.player.state
    if (ps=="paused"):
        session.player.play()
    else:
        session.player.pause()
    
def loadPlaylist(getpluri, pl):
    # Create a list with the playlists tracks
    # getpluri is full uri, pl is the playlist code

    global playlisturis
    global nooftracks
    global trackindex
    global playlist
    global lblOffline
    print "In loadPlaylist"
    print "getpluri=" + getpluri
    print "pl=" + pl
    playlist = session.get_playlist(getpluri)
    plnameenc = unicodedata.normalize('NFKD', playlist.load().name).encode('ascii', 'ignore')
    print "Playlist name: " + plnameenc

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

    nooftracks = len(playlist.tracks)
    playlisturis=[]
    for x in range(0, nooftracks):
        curtrack = str(playlist.tracks[x])
        curtrackuri = curtrack.split("'")
        playlisturis.append(curtrackuri[1])
    #print playlisturis[1]
    inttrack = int(trackindex)
    track = session.get_track( playlisturis[inttrack]).load()
    #trackindex=0
    #print track
    trackname=track.load().name
    curtrack = unicodedata.normalize('NFKD', trackname).encode('ascii', 'ignore')
    print "Playlist load, Track: " + curtrack + ", trackindex=" + trackindex
    play(curtrackuri[1])

def pldownload():
    global pl
    global playlist
    print "In pldownload"
    status["text"]= "Going to download pl"

    print "Pl:" + str(pl)
    if playlist.offline_status == 0:
        playlist.set_offline_mode(offline=True)
    else:
        playlist.set_offline_mode(offline=False)

def offline_update(dummy):
    global trackofflinestatus

    print "Offline status updated"
    #offlinestatus = playlist.offline_status
    offlinestatus=trackofflinestatus
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
    print str(offlinestatus) + ":" + offlinetxt
    lblOffline["text"]= offlinetxt

def onoffline():
    print "In onoffline"
    #spotify.connection.Connection._allow_network=False
    #spotify.ConnectionType=1
    if spotify.connection.Connection.allow_network:
        spotify.connection.Connection.allow_network=False
    else:
        spotify.connection.Connection.allow_network=True

    #print "Conn state: " + str(session.connection.state)
    #session.connection._allow_network = False
    #print "New conn state: " + str(session.connection.state)
    print spotify.connection.Connection.allow_network
    print session.connection.state
    #session.connection_state=4

def loadplaylists():
    global container
    # Load playlist container
    print "In loadplaylists"
    container = session.playlist_container
    #container.load
    while not container.load:
            pass
    print "Container loaded"
    print "You have " + str(len(container)) + " playlists."
    v=0
    for items in container:
        left = str(items)[:14]
        contItem = str(items).split(":")
        # Exclude Playlist folder entries
        if not left=="PlaylistFolder":
            #print items
            contUri = contItem[4].split("'")
            contUriuri = contUri[0]
            #print "Item uri:"  + str(v) + "----" + str(contUriuri)
            localuri = str(items).split("'")
            playlist = session.get_playlist(localuri[1])
            if not playlist.offline_status == 0:
                print localuri[1]

            v+=1


def conn_state_change(session):
    global lblSpotonline
    global onlinetext
    global spotonstatus
    #lblSpotonline["text"]="Conn state changed" - This doesnt work ,we get here before gui is set up

    print "Conn state changed: " + str(session.connection.state)
    if (root):
        #print "Window ok " + str(root)
        #if (lblSpotonline):
        spotonstatus=session.connection.state
        if (spotonstatus==1):
            onlinetext="1,Online"
        elif (spotonstatus==2):
            onlinetext="2"
        elif (spotonstatus==3):
            onlinetext="3"
        elif (spotonstatus==4):
            onlinetext="4,Offline"
        else:
            onlinetext="Error"
        #lblSpotonline["text"]=onlinetext
    if session.connection.state is spotify.ConnectionState.LOGGED_IN:
        logged_in.set()

def cleanexit():
    # Save info
    global uri
    global trackindex
    global playlistnr
    global pl
    print "In cleanexit"
    print "Username: " + username
    print "Password: " + password
    print "Playlist:" + str(pl) + "(" + str(playlistnr) + "), track " + str(trackindex)
    
    file = open("settings.py", "w")
    file.write("username=\"" + username+"\"\n")
    file.write("password=\"" + password+"\"\n")
    file.write("playlist=\"" + str(pl)+"\"\n")
    file.write("trackindex=\"" + str(trackindex)+"\"\n")
    file.write("playlistnr=\"" + str(playlistnr)+"\"\n")
    file.close()
    
    print "Bye!"
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
    global artistname, onlinetext, offlinetxt

    #print "In updateGui"

    #print "Sync status: " + str(session.offline.sync_status)
    tts=session.offline.tracks_to_sync
    #print "Tracks to sync: " + str(tts)
    #print "No of offline pls: " + str(session.offline.num_playlists)
    if tts>0:
        dltext=" " + str(tts) + " left"
    else:
        dltext=""

    lblArtist["text"]= artistname
    lblTrack["text"]= str(trackindex).zfill(2) + "-" + trackname    # zfill adds a leading 0
    lblSpotonline["text"]=onlinetext
    lblOffline["text"]= offlinetxt + dltext

    ps=session.player.state
    status["text"]=ps
    # Update Gui every second
    root.after(1000, updateGui)

def on_closing():
    cleanexit()
    root.destroy()

if __name__ == '__main__':
    #logging.basicConfig(level=logging.INFO)
    global playlistnr
    global pl, artistname, trackindex, trackname, session, offlinetxt, container
    global lblSpotonline
    artistname="Artist"
    trackindex=0
    trackname="Trackname"
    offlinetxt=""

    # Create Spotify session
    # Assuming a spotify_appkey.key in the current dir
    session = spotify.Session()
    spotonline=session.connection.state

    infotext = "6-Next tr 4-Prev tr 8-Next Pl 2-Prev pl 1-Download 5-Pause 3-On/Offline q-Quit"
    print infotext

    # Gui, uses Tkinter
    root = Tk()
    root.minsize(width=320, height=240)
    root.maxsize(width=320, height=240)

    try:
        print "Welcome to Autospot \n"
        online = internet_on()
        if online == True:
            onlinestatus="online"
        else:
            onlinestatus="offline"
        print "Online?: " + onlinestatus
    except:
        pass


    # Process events in the background
    loop = spotify.EventLoop(session)
    loop.start()

    # Events for coordination
    logged_in = threading.Event()
    logged_out = threading.Event()
    end_of_track = threading.Event()

    # Register event listeners
    session.on(spotify.SessionEvent.LOGGED_IN, on_logged_in)
    session.on(spotify.SessionEvent.END_OF_TRACK, on_end_of_track)
    #session.on(spotify.PlaylistEvent.TRACKS_ADDED, contLoaded)
    session.on(spotify.PlaylistContainerEvent.CONTAINER_LOADED, contLoaded)
    session.on(spotify.SessionEvent.OFFLINE_STATUS_UPDATED,offline_update)
    session.on(spotify.SessionEvent.CONNECTION_STATE_UPDATED, conn_state_change)

    # Create audio sink
    print "Check audio subsystem:"
    try:
        audio_driver = spotify.AlsaSink(session)
        print "Audio ok"
    except ImportError:
        #logger.warning(
        #    'No audio sink found; audio playback unavailable.')
        print "No audio sink found; audio playback unavailable."
        sys.exit()
    try:
        pl = settings.playlist
        trackindex = settings.trackindex
        strPlaylistnr=settings.playlistnr
        playlistnr = int(strPlaylistnr)
        print "We have a saved playlist"
        print "Playlist" + str(pl) + ", (" + str(playlistnr) + "), track " + str(trackindex)
    except: 
        print "Unexpected error:", sys.exc_info()[0]
        print "No playlist saved!"
        pl=""
        trackindex=0
        playlistnr=0
    try:
        username = settings.username
        password = settings.password
        print username + "-" + password
    except: 
        print "No username or password given"
        sys.exit(0)
      
    # Login
    #session.login(username, password)
    #logged_in.wait()

    remUser = session.remembered_user_name
    print "Remembered user: " + str(remUser)
    if not remUser:
      print "Wait for login " + username 
      session.login(username, password, remember_me=True)
      logged_in.wait()
    print str(session.user_name) + " is logged in"
    
    # Wait til we are online
    spotonstatus=session.connection.state
    while not (spotonstatus==1):
      pass


    """
    # Load playlist container
    container = session.playlist_container
    container.load
    while not container.load:
            pass
    print "Container loaded"
    print "You have " + str(len(container)) + " playlists."
    """
    loadplaylists()

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
        print "Uri:" + str(uri)
        #print pluser + pluri[0] # == phermansson5Lg5sAr6bKzEYCq8LbewLM
        # Should be like "'spotify:user:fiat500c:playlist:54k50VZdvtnIPt4d8RBCmZ'"
        getpluri = "spotify:user:" + pluser + ":playlist:" + pluri[0]
        #print getpluri
    else: 
        getpluri = "spotify:user:" + username + ":playlist:" + pl
        print "Using saved playlist: " + getpluri + " (Saved: " + pl + ")"
        print "Trackindex: " + str(trackindex)
    
    #getpluri is the current playlist
    loadPlaylist(getpluri, pl)

    # Gui elements

    lblInfo = Label(root,text=infotext,fg='White',bg='Grey',font=("Helvetica", 10), wraplength=300, justify=LEFT)
    lblInfo.place(width=320, height=40)
    lblInfo.pack(fill=X, side=TOP)

    lblSpotonline = Label(root,text="Spotonline",fg='Black',bg='White',font=("Verdana", 12))
    lblSpotonline.pack(fill=X, side=TOP)

    status = Label(root,text="Status",fg='Black',bg='White',font=("Verdana", 16))
    status.pack(fill=X, side=TOP)

    lblArtist = Label(root,text="Artist",fg='Black',bg='White',font=("Verdana", 20))
    lblArtist.pack(fill=X, side=TOP)

    lblTrack = Label(root,text="Track",fg='Black',bg='White',font=("Verdana", 14))
    lblTrack.pack(fill=X, side=TOP)

    lblOffline = Label(root,text="Offline status",fg='Black',bg='Yellow')
    lblOffline.pack(fill=X, side=TOP)

    # Keyboard input
    root.bind('<Key>', keyinput)
    # Update gui
    root.after(1, updateGui)

    # When window is closed
    root.protocol("WM_DELETE_WINDOW", on_closing)

    #Start gui
    # Main loop
    root.mainloop()


    """
    # Infinite loop
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
            cleanexit()
"""