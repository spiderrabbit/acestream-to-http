# acestream-to-http
Proxy to serve Acestreams as HLS progressive download 

I (and the rest of the family) are firmly into Kodi, and I've been struggling to explain Acestreams to them - and my dad likes to watch soccer on the TV. He won't do VLC reflecting but he can just about understand Kodi links!

This script serves an acestream as a progressive (HLS) video download via a .m3u8 and a Kodi .strm link. Multiple users can view the stream at the same time and it can run on reasonably low end hardware - I estimate approx 30 concurrent viewers on a HD stream on a 512MB single core at 2.2GHz. Bonus - you can opt to save the stream for later viewing.

I've also written an install script that takes a fresh Ubuntu 18.04 install and does it all for you. Only takes 5:30 mins to spin up a fresh virtual server from e.g. Digital Ocean and have it serving Acestreams.

INSTRUCTIONS TO SET UP A FRESH DIGITAL OCEAN VIRTUAL SERVER (Easy)

After logging in click on Droplets - Create

Distribution - Ubuntu 18.04

Standard droplet 1GB 1vCPU 25GB 1TB transfer

Choose a datacenter near you

Hit create (note the droplet name- you can change this if required)

Wait whilst it spins up

Use Putty or your favourite ssh client to log in to the server using the IP address that it has been assigned
username is root, password will be emailed to you- you'll be required to change this at first run


INSTRUCTIONS TO SET UP PROXY ON A FRESH 18.04 SERVER

ssh in as root with Putty or your favorite client and run

wget https://raw.githubusercontent.com/spiderrabbit/acestream-to-http/master/server_install.sh -O server_install.sh ; bash server_install.sh 

The install script will ask for a password for username "acestream", your server IP/Port and webui user/password

Done! - the script is available at r/http://SERVER*:PORT/*

NB I'm sure this will work with AWS too but not tested!


INSTRUCTIONS TO SET UP ON AN EXISTING LINUX SERVER (Advanced)

You need a web server already installed to serve the video files - Nginx or Apache

Get script from https://github.com/spiderrabbit/acestream-to-http/ (git clone or download zip file)

Make sure dependencies are installed (ffmpeg, vlc, psutil python module)

Install acestream engine (snap install?)

Alter script variables (username, password, ip, port, location of webserver directory) to suit

Alter paths in script to point to your dependency locations

Make sure webserver directory has sub directories "listings" and "segments" and is writeable by user running script. If it's not running on port 80 then update the VLC command that generates the .m3u8 file to suit.

Run as python acestream_to_http.py
