#run commands below to make permanent
echo -n "Enter PIA username:"
read username
echo -n "Enter PIA password: "
read -s password
echo
echo -n "Re-enter PIA password: "
read -s chkpassword
echo
if [ "$password" != "$chkpassword" ]; then
  echo "Passwords not same. Re-run script"
  exit
fi
echo $username > /etc/openvpn/auth.txt
echo $password >> /etc/openvpn/auth.txt

chmod a+x /home/acestream/acestream-to-http/vpn/ip_rules_allow_ssh.sh
rm /etc/rc.local
printf '%s\n' '#!/bin/bash' '/home/acestream/acestream-to-http/vpn/ip_rules_allow_ssh.sh' 'exit 0' | sudo tee -a /etc/rc.local
chmod +x /etc/rc.local

cp /home/acestream/acestream-to-http/vpn/privateinternetaccess* /etc/openvpn/
systemctl enable openvpn@privateinternetaccessUKLondon
systemctl start openvpn@privateinternetaccessUKLondon
