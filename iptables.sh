#1/bin/bash

/sbin/iptables -F INPUT
/sbin/iptables -F OUTPUT
/sbin/iptables -F FORWARD
/sbin/iptables -v -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
for port in 587 25 53; do /sbin/iptables -v -A OUTPUT -p tcp --dport $port -j ACCEPT; done
for port in 443 80 1199; do /sbin/iptables -v -A INPUT -p tcp --dport $port -j ACCEPT; done
for port in 1199 22 631; do /sbin/iptables -v -A OUTPUT -p tcp --dport $port -j DROP; done
for port in 25 587 631; do /sbin/iptables -v -A INPUT -p tcp --dport $port -j DROP; done
