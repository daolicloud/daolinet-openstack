#!/bin/bash

BRD="daolinet0"
CIDR="10.10.10.1/24"
IPTABLE="POSTROUTING -s $CIDR ! -o daolinet0 -j MASQUERADE"

if [ -z "$(brctl show | grep $BRD)" ]; then
  brctl addbr $BRD
  ip addr add $CIDR dev $BRD
fi

iptables -t nat -C $IPTABLE
if [ "$?" -ne 0 ]; then
  iptables -t nat -I $IPTABLE
fi

if   [ -n "$(vagrant box list | sed 's/(virtualbox, 0)$//' | sed 's/[ /t]*$//g' | awk '$0 =="controller"')" ]
then echo -e "\033[33m[warning]\033[0m box named \"controller\" is already exist."
else vagrant box add controller http://124.202.141.239/controller.box
fi

vagrant up
