What is DaoliNet?
=================

DaoliNet is a Software Defined Networking (SDN) system that is designed for lightweight network connections between Docker containers and virtual machines, with high availability, performance and scale-out.

Top-Level Features
------------------

* Namespace-based lightweight partition of the physical network resource on X86 servers, just like Docker's lightweight namespace partition for the CPU resource on X86 servers.

* Connecting Docker containers (and virtual machines, too) for VPCs (Virtual Private Clouds) taking place in user space without any per-configurations on host servers, and thus scale-out of Docker hosts is as simple as plug-and-play of servers with "for dummies" simplicity.

* VPCs are strictly isolated one another without running VLAN, VXLAN, GRE, iptables, etc., on any host server. This unique feature of DaoliNet not only greatly saves server resource, just like Docker using no hypervisor, but also more importantly: a VPC becomes freely distributed and scale-out spanning over different servers, datacenters, or even behind different firewalls!

Checkout our http://www.daolicloud.com

How does it work?
=================

