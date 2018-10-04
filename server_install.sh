#GENERAL INSTALL INSTRUCTIONS
#copy/paste and run the line below as root user in the ssh client (without the initial hash/ pound!):
#wget https://raw.githubusercontent.com/spiderrabbit/acestream-to-http/master/server_install.sh -O /tmp/server_install.sh; bash /tmp/server_install.sh

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

serverip=$(grep "SERVER_IP = " /home/acestream/acestream-to-http-master/acestream_to_http.py | cut -d"=" -f2 | sed 's/[^0-9a-zA-Z\.]//g')
if [ -z "$serverip" ]; then
  serverip=$(curl http://ipinfo.io/ip)
fi
echo -n "Server domain name or IP address [$serverip]: "
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
apt install -y vlc ffmpeg python-pip curl nginx unzip php7.2-fpm ufw
pip install requests psutil mediainfo
snap install acestreamplayer

sudo -u acestream wget https://github.com/spiderrabbit/acestream-to-http/archive/master.zip -O /tmp/master.zip
sudo -u acestream yes | unzip -f /tmp/master.zip -d /home/acestream/

sed -i "s/SERVER_IP = \"127.0.0.1\"/SERVER_IP = \"$serverip\"/g" /home/acestream/acestream-to-http-master/acestream_to_http.py
sed -i "s/PORT = \"4523\"/PORT = \"$port\"/g" /home/acestream/acestream-to-http-master/acestream_to_http.py
sed -i "s/USERNAME = \"user\"/USERNAME = \"$webusername\"/g" /home/acestream/acestream-to-http-master/acestream_to_http.py
sed -i "s/PASSWORD = \"acestream\"/PASSWORD = \"$webpassword\"/g" /home/acestream/acestream-to-http-master/acestream_to_http.py

cp /home/acestream/acestream-to-http-master/conf/acestream_to_http.service /lib/systemd/system/acestream_to_http.service
cp /home/acestream/acestream-to-http-master/conf/nginx.conf /etc/nginx/sites-enabled/default
rm -f /tmp/pid_stat_url
service nginx restart

systemctl daemon-reload
systemctl enable acestream_to_http.service
systemctl stop acestream_to_http.service
systemctl start acestream_to_http.service

#set up firewall
#acestream engine 62062 API commands
#acestream engine 6878 http api control
#acestream engine 8621 listening port
ufw allow 22
ufw allow 80
ufw allow 443
ufw allow 8621
ufw enable


echo server running at http://$serverip:$port - login $webusername:$webpassword 
