#GENERAL INSTALL INSTRUCTIONS
#copy/paste and run the line below as root user in the ssh client (without the initial hash/ pound!):
#wget https://raw.githubusercontent.com/spiderrabbit/acestream-to-http/master/server_install.sh ; bash server_install.sh

if [ -x $(id -u acestream) ] ; then 
  echo -n "Enter system acestream user password: "
  read -s password
  echo
  echo -n "Re-enter system acestream user password: "
  read -s chkpassword
  echo
  if [ "$password" != "$chkpassword" ]; then
    echo "Passwords not same. Re-run script"
    exit
  fi
  useradd -d /home/acestream -s /bin/bash -p $(echo $password | openssl passwd -1 -stdin) acestream
  mkdir /home/acestream
  cp -rT /etc/skel /home/acestream
  chown -R acestream:acestream /home/acestream
fi

serverip=$(curl http://ipinfo.io/ip)
echo -n "Server IP address [$serverip]: "
read serverip_temp
if [ -n "$serverip_temp" ] ; then serverip=$serverip_temp ; fi
port=4523
echo -n "Server port to run on [$port]: "
read port_temp
if [ -n "$port_temp" ] ; then port=$port_temp ; fi
webusername="user"
echo -n "Web username [$webusername]: "
read webusername_temp
if [ -n "$webusername_temp" ] ; then webusername=$webusername_temp ; fi
webpassword="acestream"
echo -n "Web password [$webpassword]: "
read webpassword_temp
if [ -n "$webpassword_temp" ] ; then webpassword=$webpassword_temp ; fi

apt update
apt install -y vlc ffmpeg python-pip curl nginx
pip install requests psutil
snap install acestreamplayer

sudo -u acestream mkdir -p /home/acestream/acestream_to_http/www/listings/
sudo -u acestream mkdir -p /home/acestream/acestream_to_http/www/segments/
sudo -u acestream echo "  
<html>
<head>
<title>Acestream Player</title>
<link href='https://unpkg.com/video.js/dist/video-js.css' rel='stylesheet'>
<script src='https://unpkg.com/video.js/dist/video.js'></script>
<script src='https://unpkg.com/videojs-contrib-hls/dist/videojs-contrib-hls.js'></script>
</head>
<body>
<video style='margin:auto' id='my_video_1' class='video-js vjs-default-skin' controls preload='auto' width='640' height='360' data-setup='{}'></video>
<script>
const player = videojs('my_video_1');
player.src({
src: '/segments/acestream.m3u8',
type: 'application/x-mpegURL'
});
</script>
</body>
</html>
" > /home/acestream/acestream_to_http/www/player.html 
sudo -u acestream wget https://raw.githubusercontent.com/spiderrabbit/acestream-to-http/master/acestream_to_http.py -O /home/acestream/acestream_to_http/acestream_to_http.py
sed -i "s/SERVER_IP = \"127.0.0.1\"/SERVER_IP = \"$serverip\"/g" /home/acestream/acestream_to_http/acestream_to_http.py
sed -i "s/PORT = \"4523\"/PORT = \"$port\"/g" /home/acestream/acestream_to_http/acestream_to_http.py
sed -i "s/USERNAME = \"user\"/USERNAME = \"$webusername\"/g" /home/acestream/acestream_to_http/acestream_to_http.py
sed -i "s/PASSWORD = \"acestream\"/PASSWORD = \"$webpassword\"/g" /home/acestream/acestream_to_http/acestream_to_http.py

echo "[Unit]
Description=Acestream Service
After=multi-user.target
Conflicts=getty@tty1.service

[Service]
Type=simple
User=acestream
ExecStart=/usr/bin/python /home/acestream/acestream_to_http/acestream_to_http.py

[Install]
WantedBy=multi-user.target" > /lib/systemd/system/acestream_to_http.service

echo "server {
	listen 80 default_server;
	listen [::]:80 default_server;
	root /home/acestream/acestream_to_http/www/;
	index index.html index.htm index.nginx-debian.html;
	server_name _;
	location / {
               autoindex on;
	}
}" > /etc/nginx/sites-enabled/default
service nginx restart

systemctl daemon-reload
systemctl enable acestream_to_http.service
systemctl stop acestream_to_http.service
systemctl start acestream_to_http.service

echo server running at http://$serverip:$port , login $webusername:$webpassword
