AutoSpot
=====

A command-line Spotify-client based on Pyspotify2. Not really usable yet.  

sudo apt-get install libffi-dev
For 32-bit:
wget https://developer.spotify.com/download/libspotify/libspotify-12.1.51-Linux-i686-release.tar.gz
Or for 64-bit:
wget https://developer.spotify.com/download/libspotify/libspotify-12.1.51-Linux-x86_64-release.tar.gz

tar zxvf libspotify*
cd libspotify*
sudo make install prefix=/usr/local

-Get a Spotify App key from https://devaccount.spotify.com/my-account/keys/ 
and store it in the current directory.
-Rename "settings_editthis" to "settings".
-Edit settings and add your Spotify credentials.
-Run. 


Package built with instructions from https://packaging.python.org/en/latest/distributing.html#setup-for-project-distributors
