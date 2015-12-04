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

vagrant box add controller http://124.202.141.239/controller.box
vagrant up
