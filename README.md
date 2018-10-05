# acestream-to-http
Proxy to serve Acestreams as HLS progressive download 

I (and the rest of the family) are firmly into Kodi, and I've been struggling to explain Acestreams to them - and my dad likes to watch soccer on the TV. He won't do VLC reflecting but he can just about understand Kodi links!

This script serves an acestream as a progressive (HLS) video download via a .m3u8 and a Kodi .strm link. Multiple users can view the stream at the same time and it can run on reasonably low end hardware - I estimate approx 30 concurrent viewers on a HD stream on a 512MB single core at 2.2GHz. Bonus - you can opt to save the stream for later viewing. The saved matches, webui and stream links are protected with HTTP AUTH and HTTPS (if you use a domain name rather than an IP e.g. noip or other dynamic DNS)

I've also written an install script that takes a fresh Ubuntu 18.04 install and does it all for you. Only takes 5:30 mins to spin up a fresh virtual server and have it serving Acestreams.


## INSTRUCTIONS TO SET UP PROXY ON A FRESH 18.04 SERVER

ssh in as root with Putty or your favorite client and run

    wget https://raw.githubusercontent.com/spiderrabbit/acestream-to-http/master/server_install.sh -O /tmp/server_install.sh; bash /tmp/server_install.sh 

The install script will ask for a password for username "acestream", your server IP/Port and webui user/password

Done! - the script is available at http://SERVER:PORT/

VPN

## VPN Support

This package comes with a prebuilt set of rules for Private Internet Access VPN. Simply (as root) go to the vpn subdirectory and run

    install_vpn_service.sh
    
and enter your PIA username/ password. This will install ip tables routes and rules to allow ssh and HTTP access to the public ip of your server but will bind the acestream engine to a VPN which will run on restart as a service. (check with lsof -i). By default it chooses the UK London server; you can change this by altering vpn/privateinternetaccess.conf and entering a server closer to you: [PIA list of servers](https://www.privateinternetaccess.com/pages/network/)



## INSTRUCTIONS TO SET UP ON AN EXISTING LINUX SERVER (Advanced)

You need a web server already installed to serve the video files - Nginx or Apache

Get script from https://github.com/spiderrabbit/acestream-to-http/ (git clone or download zip file)

Make sure dependencies are installed (ffmpeg, vlc, psutil python module)

Install acestream engine (snap install?)

Alter script variables (username, password, ip, port, location of webserver directory) to suit

Alter paths in script to point to your dependency locations

Make sure webserver directory has sub directories "listings" and "segments" and is writeable by user running script. If it's not running on port 80 then update the VLC command that generates the .m3u8 file to suit.

Run as python acestream_to_http.py
