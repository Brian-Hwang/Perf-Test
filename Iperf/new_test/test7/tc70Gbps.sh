#!/bin/bash

# The interface name
IFACE="enp6s0"

# The bandwidth limit (in kbps)
BW_LIMIT="50Gbit"

# Delete the existing qdisc
sudo tc qdisc del dev $IFACE root

# Add a new root qdisc
sudo tc qdisc add dev $IFACE root handle 1: htb default 10

# Add a child qdisc with rate limiting
sudo tc class add dev $IFACE parent 1: classid 1:1 htb rate $BW_LIMIT
sudo tc class add dev $IFACE parent 1:1 classid 1:10 htb rate $BW_LIMIT

