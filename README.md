DaoliNet for Lightweight Docker Networking
=================

DaoliNet is a Software Defined Networking (SDN) system that is designed for lightweight network connections for Docker containers, with high availability, performance and scale-out.

Top-Level Features
------------------
* Lightweight connection of Docker containers, non-communication containers do not consume server resource, just like Docker's lightweight virtualization of containers without the extra load of a hypervisor, means you can get more out of your hardware resource.

* Connected containers can be distributed over a swarm of Docker hosts anywhere, which can be laptops or PCs inside the firewalls of your office or home, virtual machines or servers in your own datacenter, or even in public clouds such as AWS. Trans-datacenter traffic is always encrypted.

* Ease of resource pooling by plug-and-play adding Docker hosts.

* Pure software implementation using Open-V-Switch (OVS) which is ubiquitously available in every Linux server, providing network functions as distributed switches, routers, gateways and firewalls.

**More in our website**:  http://www.daolicloud.com

Docker in Need of Lightweight Networking
=================

Docker is awesome! It is a container engine to virtualize server CPUs much more efficient than a hypervisor does for virtual machines (VMs). A Docker host can partition an X86 server into thousands of containers. Containers are playing more and more roles in cloud computing in place of VMs. However, because each Docker host is created independently from one another, containers in different Docker hosts are by default not connected one another. We need an efficient and lightweight networking solution to connect containers which are distributed in multiple Docker hosts.

Existing Solutions
------------------
There exists a number of offers for Docker networking: Weave, Flannel, and Calico are well-known open source projects for Docker networking. Calico and Weave, require that each Docker host must provide the full function of a router to perform route discovery and state update with other Docker hosts as routers; this is unfortunately very heavyweight in resource utilization. Flannel requires that Docker hosts run packet encapsulation, e.g., VXLAN, to tunnel container packets in-between different Docker hosts; packet encapsulation not only consumes extra load of hardware resource (VXLAN is also known as "network hypervisor"), but also nullifies useful network diagnosing and troubleshooting tools such as traceroute. To date, networking is a core feature of Docker that is relatively immature and still under heavy development.

How DaoliNet Works
==================

The DaoliNet is based on OpenFlow Standard. With DaoliNet, Docker hosts do not learn and update routing information from one another; also they are not configured to run encapsulation protocols between them. All a Docker host has to know for networking is an OpenFlow Controller. This simple not-knowing-one-another relationship among Docker hosts greatly simplifies the management and scalability of Docker cloud. Below let us provide an introduction to important advantages which are enabled by OpenFlow.

OpenFlow Technology
-------------------
OpenFlow is an industry standard networking technology. It uses an OpenFlow Controller (below is shortened to the Controller) which is a logically centralized entity but physically a set of HA distributed web-service-like agents.

Upon a container initiation of a connection, its Docker host will "PacketIn" by sending the first packet from the container to the Controller. The Controller will respond with "PacketOut" by issuing flows to the involved Docker hosts for them to establish the connection (assuming that the connection involves containers over different Docker hosts).

The automatic PacketIn by a Docker host to lift the first packet to the Controller, and the PacketOut real-time routing configuration of involved Docker hosts are functions of Open-v-Switch (OVS) which is a standard kernel component in every Linux OS.

With the use of the Controller, Docker hosts in the system can be in a simple state of not-knowing-one-another. This greatly simplifies the management of Docker hosts for provisioning service HA and LB. There is no need for the Docker hosts to run complex and resource consuming routing algorithms. There is also no need for the Docker hosts to pairwise run a packet encapsulation protocol which is not only resource consuming but also nullifies network diagnosing and troubleshooting tools such as traceroute.

Summary of DaoliNet Architecture
================================
In a DaoliNet network, all compute servers are in an ethernet which is either physically connected by switches, or by VPN connected. Each compute server acts as a router for all of the endpoints that are hosted on that compute server. However, such a router is not an intelligent one in that it never establishes any routing relationship with any other routers in the system. The data path is implemented by the OVS. The control plane is provided by the Controller which, upon a connection request by an OVS implemented non-intelligent router, real-time configures a pair of such routers to establish a hot-plug flow based connection.

Lightweight Networking for Containers
====================================
Non-intelligent routers consume little server resource since they never run any routing algorithm. Moreover, if a connection is idle for a threshold of time, the flows relating to the idle connection will age and be deleted from the memory; then the involved Docker hosts return to the original state not-knowing-each-other. This no-connection, no-resource-consumption style of server resource utilization is in the same lightweight fashion of the Linux Container technology in that an idling container consumes little server resource. Therefore, DaoliNet is a lightweight networking technology for connecting Docker containers.

**More in our website:** http://www.daolicloud.com/html/technology.html
