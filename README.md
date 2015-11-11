What is DaoliNet?
=================

DaoliNet is a Software Defined Networking (SDN) system that is designed for providing lightweight connections between Docker containers and virtual machines, with high availability, performance and scale-out.

Top-Level Features
------------------

* Namespace-based lightweight partition of the physical network resource of X86 servers, just like Docker's lightweight namespace partition for the CPU resource of X86 servers.

* Connecting Docker containers (and virtual machines too) for VPCs (Virtual Private Clouds) taking place in user space without any per-configurations for Docker host servers, and thus scale-out of Docker hosts is as simple as plug-and-play with "for dummies" simplicity.

* Cloud VPCs are strictly isolated one another without running VLAN, VXLAN, GRE, iptables, etc., on any servers. This unique feature of DaoliNet not only greatly saves server resource, just like Docker's without running hypervisors on servers, but also more importantly: a cloud VPC become freely distributed and scaled-out to span over different servers, datacenters, and even behind different firewalls!

Checkout our http://www.daolicloud.com
