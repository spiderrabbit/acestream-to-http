# if setting up vpn then these commands allow ssh access and starts vpn
# https://serverfault.com/questions/659955/allowing-ssh-on-a-server-with-an-active-openvpn-client
rm /etc/resolv.conf
echo nameserver 8.8.8.8 > /etc/resolv.conf
current_ip=$(ip route get 1 | grep -Po '(?<=src )(\S+)')
current_gw=$(ip -4 route ls | grep default | grep -Po '(?<=via )(\S+)')
ip rule add from $current_ip table 128
ip route add table 128 to $current_ip/32 dev $(ip -4 route ls | grep default | grep -Po '(?<=dev )(\S+)')
ip route add table 128 default via $current_gw

#run commands below to make permanent
#rm /etc/rc.local
#printf '%s\n' '#!/bin/bash' '/home/acestream/acestream-to-http-master/vpn/ip_rules_allow_ssh.sh' 'exit 0' | sudo tee -a /etc/rc.local
#sudo chmod +x /etc/rc.local
