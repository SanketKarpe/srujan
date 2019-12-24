# Installation steps for Srujan
## OS requirements
Install latest version of Raspbian on Raspberry Pi 3 or 4

## Packages to install
<code>
sudo apt install isc-dhcp-server
</code>
<code>
pip install -r requirements.txt
</code>
  
## Hardware requirements
Use any USB 3.0 to RJ45 Gigabit Ethernet Network Adapter ( Can be skipped for Raspberry Pi 4 )
  
## Configuration
Configure DHCP server to provide static IP on different subnets to eth0 and eth1
Add route from eth0 to eth1 using <code>ip route add 192.168.1.0/24 via 192.168.10.1 </code> 

