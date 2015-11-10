# DaoliNet Network Virtualization

The DaoliNet Network Virtualization is based on Openflow Standard, which completely separates the control plane and forward plane for your virtualized cloud network. Below let us provide a in-a-nut-shell introduction to the control-forward separation and important advantages.

Openflow Controller
===================

This is a set of distributed deployed web service agents. They receive "PacketIn" request from the forward plane, which is a normal communication packet that forwarding devices do not know how to process switching/routing/gateway-in-out/firewall-in-out, and answer with "PacketOut" which is flow information to on-the-fly configure the forwarding devices turning them into intelligent to forward the packets.

Forwarding Devices
==================

The DaoliNet forwarding devices are standard x86 servers running Linux kernel with Open-v-Switch (OVS) agents without any pre-confirguration apart from only knowing the Openflow Controller. This means that the deployment of the forwarding devices completely independent of one another, in fact, the forwarding devices forming a cloud network do not know one another at all, each device only knows the Openflow Controller. Once on-the-fly PacketOut configured by the Controller, the forwarding devices become intelligent to execute network functions of switching (L2), routing (L3) and gateway-ing (L4: NAT-in-out, Firewall-in-out), and can form security groups for your virtual private cloud (VPC), and handle load balancing function at the edge of your cloud network.

Advantages:
-----------

* Maximum Flexibility: DaoliNet Network Virtualization does not use VLAN in L2, however the cloud tenants' VPCs are completed isolated in L2; and not use any packet encapsulation (such as VXLAN, GRE, etc) in trans-L2 scale out your cloud network. This unique feature of DaoliNet enables trans-Docker-host connecting Docker containers in the same lightweight spirit of Docker containers, and the connection has "for dummies" simplicity.
* Since all devices in DaoliNet are fully distributed, you can easily scale out your L2/L3/L4 services by simply adding more x86 servers to your physical underlay network, they can be added in separate datacenters, and can even be added behind separate physical firewalls!
