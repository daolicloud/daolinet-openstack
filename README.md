What is DaoliNet?
=================

DaoliNet is a Software Defined Networking (SDN) system that is designed for lightweight network connections between Docker containers and virtual machines, with high availability, performance and scale-out.

Top-Level Features
------------------

* Namespace-based lightweight partition of the physical network resource on X86 servers, just like Docker's lightweight namespace partition for the CPU resource on X86 servers.

* Connecting Docker containers (and virtual machines, too) for VPCs (Virtual Private Clouds) taking place in user space without any per-configurations on host servers, and thus scale-out of Docker hosts is as simple as plug-and-play of servers with "for dummies" simplicity.

* VPCs are strictly isolated one another without running VLAN, VXLAN, GRE, iptables, etc., on any host server. This unique feature of DaoliNet not only greatly saves server resource, just like Docker using no hypervisor, but also more importantly: a VPC becomes freely and dynamically distributed and scale-out spanning over different servers, datacenters, or even behind different firewalls!

Checkout our website  http://www.daolicloud.com

How does it work?
=================

DaoliNet Network Virtualization
-------------------------------

The DaoliNet Network Virtualization is based on Openflow Standard, which completely separates the control and forward planes for your virtualized cloud network. Below let us provide an introduction to important advantages enabled by Openflow.

Openflow Controller
-------------------

This is a set of distributed web service agents. They receive a "PacketIn" request from a server host and reply a "PacketOut" response to the requesting server. A packetin request is a normal network packet that the server receives but does not know how to process switching/routing/gateway-in-out/firewall-in-out, due to lack of configuration intelligence. A packetout response from the Controller is a flow which on-the-fly configures the packetin server to turn it into intelligent for forwarding packets.

Host Servers as Forwarding Devices
----------------------------------

The DaoliNet uses standard X86 servers running Linux kernel with Open-v-Switch (OVS) agents as networking forwarding devices. When joining a cloud resource pool, a server has no any networking confirguration apart from only knowing the IP addresses of Openflow Controllers. This means that the servers joining a cloud resource pool are completely independent of one another, having no whatever knowledge of one another at all. Once on-the-fly configured by the Controller, a server becomes intelligent to forward packets in various network functions, e.g., switching (L2), routing (L3) and gateway-ing (L4: NAT-in-out, Firewall-in-out), and can also form security groups for a cloud tenant, and handle load balancing at the edge of a cloud network.

