DaoliNet for Efficient and Dynamic Docker Networking
=================

DaoliNet is a Software Defined Networking (SDN) system that is designed to provide efficient and dynamic connection for Docker containers, which is suitable for the lightweight and ephemeral nature of micro-servicing workloads of Docker containers.

Top-Level Features
------------------
* Resource efficiency: Connection of containers does not consume server resource when the containers are not in active communication. You get more out of your server resource.

* Distribution anywhere: Docker servers can be laptops or PCs inside the firewalls of your office or home, servers in your own datacenter, or virtual machines in public clouds such as AWS. Trans-datacenter traffic is always encrypted.

* Network virtualization: You can choose any CIDR IP addresses for your containers, and a container can keep IP address unchanged after moving physical locations.

* Multi-tenancy isolation: Networks of different tenants are completely isolated from one another.

* Pure software implementation using Open-V-Switch (OVS): Providing network functions as distributed switches, routers, gateways and firewalls. System deployment in a plug-n-play simplicity.

**More in our website**:  http://www.daolicloud.com

Docker in Need of Efficient and Dynamic Networking
=================

Docker is awesome! It is a container engine to virtualize server CPUs much more efficient than a hypervisor does for virtual machines (VMs). A Docker server can partition an X86 server into thousands of containers. Containers are playing more and more roles in cloud computing in place of VMs. However, because each Docker server is created independently from one another, containers which are distributed in different Docker servers are by default not connected one another. We need a network solution to connect Docker containers.

We know that containers are highly efficient in resource utilization, and ephemeral in lifecycle due to their suitability for micro-services provisioning. These properties translate to a large number of dynamic containers in a Docker cloud. A networking solution for Docker, if not very carefully designed, would tarnish the efficiency of Docker cloud. Unfortunately, some well-known networking techniques such as MAC-in-UDP encapsulation, or Docker servers running routing algorithms, do fall into such pitfalls. MAC-in-UDP encapsulation flattens a container network and causes Docker servers to store and process a large number of MAC addresses of containers. Docker servers running routing algorithms mean that they have to frequently discover and update dynamic route tables. Either is very inefficient in server resource utilization.

To date, networking is a core feature of Docker that is relatively immature and still under heavy development.

DaoliNet for Efficient and Dynamic Docker Networking
==========================================

Architecture
------------
The networking architecture of DaoliNet is based on the OpenFlow standard. It uses an OpenFlow Controller as the control plane, and Open-V-Switches (OVSes) to implement the datapath. The OpenFlow Controller in DaoliNet is a logically centralized entity but physically a set of HA distributed web-service-like agents. OVSes are ubiquitously available in Linux kernels and hence in all Docker servers.

In a DaoliNet network, all Docker servers are in an Ethernet which is either physically or VPN connected. Each Docker server acts as a virtual router for all of the container workloads that are hosted on that server. However, these virtual routers work in OpenFlow technology and they do not run any routing algorithms; in fact they even do not know the existence of one another. Each virtual router only knows the OpenFlow Controller. Upon a container initiating a connection, the involved virtual routers will be real-time configured by the OpenFlow Controller to establish a route.

How it Works
------------
When a container initiates a connection, the OVS in the hosting Docker server as the source router will issue a PacketIn request to the OpenFlow Controller. The PacketIn request is just the first packet from the initiating container. The OpenFlow Controller, knowing all Docker servers as OpenFlow routers in the system and seeing PacketIN, can identify another Docker server which hosts the container as the destination workload. This second Docker server is the destination router for the connection. The OpenFlow Controller will respond with a pair of PacketOut flows, one for the source router, and the other for the destination router. These two flows provide real-time configurations for the two routers to establish a route for the requested connection. In case the two containers are in the same Docker server, the source and destination router is just the same server.

The OpenFlow established connection is in a hot-plug fashion in that, the involved routers have not run any routing algorithm to learn and propagate routing tables. It is the OpenFlow Controller that adds the route information to the respective routers. Also, if a connection becomes idle and upon a time threshold, the hot-plug route flows for the idle connection will time-out and be deleted from the memory of the involved routers. Therefore the routers in DaoliNet are non-intelligent ones, they work in a no-connection, no-resource-consumption style of resource utilization. This style of resource utilization is very similar to the Linux Container technology utilizing server CPU in that, an idling container consumes little server resource. DaoliNet is an efficient and dynamic networking technology for connecting Docker containers.

Simple Networking for Containers
--------------------------------
In DaoliNet, Docker servers in the system are in a simple state of not-knowing-one-another, completely independent from one another. This architecture not only conserves resource utilization, but more importantly the independent relationship among the Docker servers greatly simplifies the management of resource. Extending the resource pool is as simple as plug-n-play style of adding a server to the pool and notifying the OpenFlow Controller. No complex routing table discovery and update among the routers is needed. There is also no need for Docker servers to pairwise run some packet encapsulation protocol which is not only inefficient in resource utilization but will also nullify network diagnosing and troubleshooting tools such as traceroute.

**More in our website:** http://www.daolicloud.com/html/technology.html
