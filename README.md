What is DaoliNet?
=================

DaoliNet is a Software Defined Networking (SDN) system that is designed for lightweight network connections for Docker containers, with high availability, performance and scale-out.

Top-Level Features
------------------

* Lightweight and highly efficient virtualization of the network resource on X86 servers, just like Docker's lightweight and highly efficient partition of the CPU resource on X86 servers.

* Docker containers are connected to form VPCs (Virtual Private Clouds) and security groups without any pre-configuration of the participating Docker hosts. Any Docker host has no knowledge of containers in other Docker hosts. Thus scale-out deployment of Docker hosts has a plug-and-play "for dummies" simplicity.

* Overlay network of containers is constructed without using packet encapsulation technologies such as VLAN, VXLAN, GRE, etc. This unique feature of DaoliNet not only greatly saves server resource, just as Docker saves server resource without using hypervisors, but also more importantly simplifies cloud management: an overlay network of containers can be constructed in user-mode and hot-plug manner, can span over different Docker hosts, datacenters, or even behind different firewalls, irrespective of locations of the containers.

* Pure software implementation, with high availability distribution over any underlying physical network, and plug-and-play easy adding servers to the resource pool.


**More in our website**:  http://www.daolicloud.com

![DaoliNet Topology](http://www.daolicloud.com/static/topology.png)

Docker Networking
=================

Docker is awesome! It is a container engine to virtualize server CPUs much more efficient than a hypervisor does for virtual machines (VMs). A Docker host can partition an X86 server into thousands of containers. Containers are playing more and more roles in cloud computing in places of VMs. However, because each Docker host is created independently one another, containers in different Docker hosts by default are not connected one another. We need an efficient and lightweight network solution to connect containers which are distributed in multiple Docker hosts.

Existing Solutions
------------------

There exists a number of offers for the Docker networking: Weave, Flannel, Libnetwork, and Colico are open source projects on Docker networking. Some of these offers require that each Docker host participating in a cloud must know the network topology of all containers in the cloud; e.g, Colico requires that containers have external IP addresses which are visible from outside of their Docker host; others require that Docker hosts run packet encapsulation, e.g., VXLAN, to tunnel overlay container packets inbetween different Doker hosts (e.g., Flannel). However, Docker hosts are created independently from each other, requiring Docker hosts to know the network information of containers in all other Docker hosts will complicate cloud management. Also packet encapsulation is similar to running a "networking hypervisor" which is somewhat against the lightweight nature of Docker. In fact, the simplest and preferred network mode for Docker is Network Address Translation (NAT) in which containers in a Docker host do not have externally visible IP addresses; when they communicate with outside world, the Docker host will use its own IP address to NAT translate the internal IP addresses of containers. DaoliNet adopts this simple network mode without having to assign externally visible IP addresses to containers. Also DaoliNet uses no heavyweight packet encapsulation or "networking hypervisor" method.

How DaoliNet Works
==================

DaoliNet Network Virtualization
-------------------------------

The DaoliNet Network Virtualization is based on Openflow Standard, which completely separates the control and forward planes for your virtualized cloud network. With DaoliNet, Docker hosts are created and managed independently; there is no deed for them to know one another. This greatly simplifies the management and scalability of Docker cloud. Below let us provide an introduction to important advantages enabled by Openflow.

Openflow Controller
-------------------

This is a set of distributed web service agents. They receive a "PacketIn" request from a Decker host and reply a "PacketOut" response to the requesting host. A packetin request is a normal network packet that a Docker host receives from a container but does not know how to process switching/routing/gateway-in-out/firewall-in-out, due to lack of configuration intelligence. A packetout response from the Controller is a flow which configures in real time the packetin host to turn it into intelligent for forwarding packets.

Servers as Networking Boxes for Distributed Switches, Routers, Gateways, and Firewalls
---------------------------

The DaoliNet uses standard X86 servers running Linux kernel with Open-v-Switch (OVS) as networking forwarding devices. When joining a cloud resource pool, a server has no any networking confirguration information apart from only knowing the IP addresses of the Openflow Controllers. This means that the Docker hosts joining a cloud resource pool are completely independent of one another, having no whatever knowledge of one another at all. Once real-time configured by the Controller, a Docker host becomes intelligent to forward packets in various network functions, e.g., switching (L2), routing (L3) and gateway-ing (L4: NAT-in-out, Firewall-in-out), and can also form security groups for a cloud tenant, and handle load balancing at the edge of a cloud network.

Overlay Network for Distributed Containers
------

When a container is created in a Docker host server, its network medadata will be captured by DaoliNet Openflow Controller (below we use the Controller for short). The network metadata include: the container's MAC address, the container's IP address, the server's intranet MAC, the server's intranet IP, and the default gateway IP (the default gateway is the server). The Controller will also capture the security group information of the container, i.e., information about a group of containers belonging to one security group, which is specified by the owner of the containers.

When a container (say C1 in the figure below) initiates a communication session to another container (C2), packets from C1 are received by the Docker host (Server1) for to forward to C2 (hosted by Server2). However, Server1 has no switching, routing, or gatewaying information for these packets. In Openflow standard, the OVS in Server1 will ask for help from the Controller by lifting the first packet to the Controller. This packet-lift-to-controller event is called packetin (see PacketIn1 in the figure below).

![Workflow](http://www.daolicloud.com/static/workflow.png)

The packetin lifted to the Controller contains sufficient network metadata: source MAC and IP addresses of C1, destination MAC and IP addresses of C2, plus those of Server1 and Server2. Suppose that the Controller judges from security policy that C1 and C2 can legally communicate, it will respond to Server1 with packeout (PacketOut1), which is a flow sent to Server1 to real-time configure the server. In addition, the Controller will also send a corresponding flow to Server2 as a real-time configuration (PacketOut2). Upon receipt the respective flows by Server1 and Server2, the OVS-es in these two Docker hosts become knowing how to forward the packets, and the Controller will not be contacted any more for the remainder communications session.

The above pair of flows uniquely define a session of connection between C1 and C2 irrespective of the locations of C1 and C2. Let's analyse the following two cases. Case 1: C1 and C2 being in the same Docker host (Server1 = Server2), the pair of flows are MAC address defined. Case 2: C1 and C2 being in different Docker hosts (Server1 =\= Server2), the flow for Server1 is NAT-out, and that for Server2 is NAT-in, and both flows are identified by the src port number of C1, which is a randum number created by C1. We also notice that there is no need for C1 and C2 being in the same subnet, this is because the OVS-es form distributed and ubiquitous routers in every Docker host!

NAT-out from a container to a node in the Internet, and Firewall-ingress from an Internet node to a container can also be on-the-fly established by the Controller.

**More in our website**: http://www.daolicloud.com/html/technology.html

**SlideShare** http://www.slideshare.net/daolinetppt/daolinet-lightweight-and-simple-networking-for-docker
