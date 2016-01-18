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


An OpenFlow Architecture of DaoliNet
=========
OpenFlow is an industry standard networking technology. A network with the OpenFlow architecture uses an OpenFlow Controller as the control plane, and Open-V-Switches (OVSes) to implement the datapath. The OpenFlow Controller is a logically centralized entity but physically a set of HA distributed web-service-like agents. The OVSes in DaoliNet are ubiquitously available in Linux kernels and hence in all Docker hosts.

In a DaoliNet network, all compute servers (Docker hosts) are in an Ethernet which is either physically or VPN connected. Each compute server acts as a router for all of the container workloads that are hosted on that compute server.

How it Works
------------
When a container initiates a connection, the OVS in the hosting Docker host, i.e., the source router, will issue a PacketIn request to the OpenFlow Controller. The PacketIn request is just the first packet from the initiating container. The OpenFlow Controller who knows all Docker hosts in the system can identify, from the PacketIn packet, another Docker host which hosts a container as the destination workload for the connection, to be the destination router for the connection. The OpenFlow Controller will respond with a pair of PacketOut flows, one for the source router, and the other, the destination router, for them to establish a route for the requested connection. In case the two containers are in the same Docker host, the source and destination router is just the same Docker host.

We notice that such a connection is hot-plug based in that, the two routers are non-intelligent ones; they do not run conventional routing algorithms, and do not learn and propagate routing tables. In fact, prior to a connection, the routers do not know each other. Also, if a connection becomes idle for a threshold of time, the flow based route for the idle connection will age and be deleted from the memory of the routers; then the involved routers return to the original state of not-knowing-each-other. Therefore, the flow based route is in a no-connection, no-resource-consumption style of resource utilization. The non-intelligent routers in DaoliNet work in the same lightweight fashion of the Linux Container technology in that an idling container consumes little server resource. Therefore, DaoliNet is a lightweight networking technology for connecting Docker containers.

Lightweight and Simple Networking for Containers
----------
In OpenFlow architecture, Docker hosts in the system are in a simple state of not-knowing-one-another, completely independent from one another. This architecture not only conserves resource utilization, but more importantly the independent relationship among the Docker hosts greatly simplifies the management of resource. Extending a resource pool is as simple as plug-and-play style of adding Docker host to the pool and notifying the OpenFlow Controller. No complex routing state updating with the rest of the routers is needed. There is also no need for the Docker hosts to pairwise run some packet encapsulation protocol which is not only resource consuming but also nullifies network diagnosing and troubleshooting tools such as traceroute.

**More in our website:** http://www.daolicloud.com/html/technology.html
