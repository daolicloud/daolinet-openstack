DaoliNet for Lightweight Docker Networking
=================

DaoliNet is a Software Defined Networking (SDN) system that is designed for lightweight network connections for Docker containers, with high availability, performance efficiency and scale-out.

Top-Level Features
------------------
* Resource efficient connection for Docker containers: connection of containers does not consume server resource when the containers are not in active communication. You get more out of your server resource.

* Connected containers can be distributed over a swarm of Docker servers anywhere, including laptops or PCs inside the firewalls of your office or home, servers in your own datacenter, or virtual machines in public clouds such as AWS. Trans-datacenter traffic is always encrypted.

* Elastic expansion of resource pool for dummies: plug-n-play adding Docker servers with zero confirguration.

* Pure software implementation using Open-V-Switch (OVS) providing network functions as distributed switches, routers, gateways and firewalls.

**More in our website**:  http://www.daolicloud.com

Docker in Need of Lightweight Networking
=================

Docker is awesome! It is a container engine to virtualize server CPUs much more efficient than a hypervisor does for virtual machines (VMs). A Docker server can partition an X86 server into thousands of containers. Containers are playing more and more roles in cloud computing in place of VMs. However, because each Docker server is created independently from one another, containers in different Docker hosts are by default not connected one another. We need an efficient and lightweight networking solution to connect containers which are distributed in multiple Docker servers.

Existing Solutions
------------------
There exists a number of open source projects for Docker networking: Weave, Flannel, and Calico are well-known ones. Calico and Weave, require that a Docker server must provide the full function of a router to discover and update route tables with other Docker servers as routers in the system. Routing algorithms are very heavyweight in resource consumption. Flannel requires that Docker hosts run packet encapsulation, e.g., MAC in UDP, to tunnel container packets in-between different Docker servers. Packet encapsulation not only consumes extra load of hardware resource (e.g., VXLAN is also known as "network hypervisor"), but also nullifies useful network diagnosing and troubleshooting tools such as traceroute, etc. To date, networking is a core feature of Docker that is relatively immature and still under heavy development.

DaoliNet for Lightweight Docker Networking
==========================================

Architecture
------------
The networking architecture of DaoliNet is based on the OpenFlow standard. It uses an OpenFlow Controller as the control plane, and Open-V-Switches (OVSes) to implement the datapath. The OpenFlow Controller in DaoliNet is a logically centralized entity but physically a set of HA distributed web-service-like agents. OVSes are ubiquitously available in Linux kernels and hence in all Docker servers.

In a DaoliNet network, all Docker servers are in an Ethernet which is either physically or VPN connected. Each Docker server acts as a router for all of the container workloads that are hosted on that server. However, the routers do not run any routing algorithms and so they do not know one another. Each router only knows the OpenFlow Controller. Upon a container initiating a connection, the involved routers will be real-time configured by the OpenFlow Controller to establish a route.

How it Works
------------
When a container initiates a connection, the OVS in the hosting Docker server as the source router will issue a PacketIn request to the OpenFlow Controller. The PacketIn request is just the first packet from the initiating container. The OpenFlow Controller, knowing all Docker servers as routers in the system and seeing PacketIN, can identify another Docker server which hosts a container as the destination workload. This second Docker server is the destination router for the connection. The OpenFlow Controller will respond with a pair of PacketOut flows, one for the source router, and one for the destination router. These two flows provide real-time configurations for the two routers to establish a route for the requested connection. In case the two containers are in the same Docker server, the source and destination router is just the same server.

The OpenFlow established connection is in a hot-plug fashion in that, the involved routers have not run routing algorithms to learn and propagate routing tables. It is the OpenFlow Controller that adds the routing information to the respective routers in PacketOut time. Also, if a connection becomes idle and upon a time threshold, the hot-plug route flows for the idle connection will overtime and be deleted from the memory of the involved routers. Therefore the routers in DaoliNet are non-intelligent ones, they work in a no-connection, no-resource-consumption style of resource utilization. This style of resource utilization is very similar to the Linux Container technology utilizing server CPU in that, an idling container consumes little server resource. DaoliNet is a lightweight networking technology for connecting Docker containers.

Simple Networking for Containers
--------------------------------
In DaoliNet, Docker servers in the system are in a simple state of not-knowing-one-another, completely independent from one another. This architecture not only conserves resource utilization, but more importantly the independent relationship among the Docker servers greatly simplifies the management of resource. Extending the resource pool is as simple as plug-n-play style of adding a server to the pool and notifying the OpenFlow Controller. No complex routing table discovery and update among the routers is needed. There is also no need for Docker servers to pairwise run some packet encapsulation protocol which is not only inefficient in resource utilization but will also nullify network diagnosing and troubleshooting tools such as traceroute.

**More in our website:** http://www.daolicloud.com/html/technology.html
