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

![](http://www.daolicloud.com/static/topology.png)

**Figure 1, DaoliNet Topology**

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

Servers Playing the Roles of Network Devices
---------------------------

The DaoliNet uses standard X86 servers running Linux kernel with Open-v-Switch (OVS) as networking forwarding devices. When joining a cloud resource pool, a server has no any networking confirguration information apart from only knowing the IP addresses of the Openflow Controllers. This means that the Docker hosts joining a cloud resource pool are completely independent of one another, having no whatever knowledge of one another at all. Once real-time configured by the Controller, a Docker host becomes intelligent to forward packets in various network functions, e.g., switching (L2), routing (L3) and gateway (L4: NAT-in-out, and Firewall), and can also form security groups for a cloud tenant, and handle load balance at the edge of a cloud network.

Overlay Network for Distributed Containers
------

When a container is created in a Docker host server, its network medadata will be captured by DaoliNet Openflow Controller (below we use the Controller for short). The network metadata include: the container's MAC address, the container's IP address, the server's intranet MAC, the server's intranet IP, and the default gateway IP (the default gateway is the server). The Controller will also capture the security group information of the container, i.e., information about a group of containers belonging to one security group, which is specified by the owner of the containers.

When a container (say C1 in Figure 2 below) initiates a communication session to another container (C2), packets from C1 are received by the Docker host (Server1) for to forward to C2 (hosted by Server2). However, Server1 has no switching, routing, or gatewaying information for these packets. In Openflow standard, the OVS in Server1 will ask for help from the Controller by lifting the first packet to the Controller. This packet-lift-to-controller event is called packetin (see PacketIn1 in the figure below).

![](http://www.daolicloud.com/static/workflow.png)

**Figure 2, NAT-NAT Flow**


The packet-in to the Controller contains network metadata which suffice the Controller to judge whether or not two containers are allowed to communicate. The metadata include: src-MAC and src-IP of C1, dst-MAC and dst-IP of C2, plus those of Server1 and Server2. Suppose that the Controller judges from security group policy that C1 and C2 are allowed to communicate, it will respond to Server1 with packeout (PacketOut1), which is a flow sent to Server1 to real-time configure the server. In addition, the Controller will also send a corresponding flow to Server2 as a real-time configuration (PacketOut2). Upon receipt the respective flows by Server1 and Server2, the OVS-es in these Docker hosts become knowing how to forward the packets, and the Controller will not be contacted any more for the remainder communications session.

The above pair of flows uniquely define a session of connection between C1 and C2 irrespective of their locations. Let's analyse the following two cases:

Case 1: C1 and C2 are in the same Docker host
---
In this case, Server1 = Server2. The flow packet-out to the Docker Server is MAC address defined, i.e., a switch flow, very simple! (Notice that if Controller judges that C1 and C2 are not allowed to communicate, then it will not packet-out a mac flow to the Docker Server, and thereby C1 and C2 will not be able to communicate eventhough they are in the same Docker Server!)

Case 2: C1 and C2 are in different Docker hosts:
---
In this case, Server1 =\= Server2. Two flows will be packet-out to Server1 and Server2, respectively. The flow for Server1 is NAT-out, and that for Server2 is NAT-in. Notice that both NAT flows are identified by the src-PORT of the communications initiator, i.e., C1 in Figure 2. This src-PORT of C1 is a randum number created by C1. With these two flows, C1 and C2 are connected. With NAT flows, the packets travelling between the two Docker servers use the underlay IP addresses of the two servers, and the packets travelling between a container and its hosting server use overlay IP address of the container, respectively.

OVS Forms Distributed Routers
---
We notice that there is no need for the IP addresses of C1 and C2 to be in the same subnet. In the case of C1, C2 belonging to different subnets, the OVS-es form distributed and ubiquitous routers in every Docker host.

OVS Forms Distributed Gateways
---
NAT-out from a container to a node in the Internet, and Firewall-ingress from an Internet node to a container can also be hotplug established by the Controller as real-time packet-out NAT flows. Such a NAT flow is also identified by src-PORT of a communications initiator.

Network Virtualization
---
In DaoliNet, overlay network for distributed containers is virtualized for each pair of containers which are allowed to communicate according to security group policy. The communications initiator, e.g., C1 in Figure 2, upon initiation a communications session will cause its Docker host, e.g., Server1 in Figure 2, to packet-in the request to the Controller who upon seeing C1, C2 in the same security group will packet-out a pair of NAT-NAT flows to the respective Docker hosts. Containers in different security groups are network isolated from one another by different src-port numbers of the respective requestors. The Controller can see the relationship between a src-port number and the network identity in packet-in. 

No Packet Encapsulation, No Firewall Chokepoint
---
Docker is a lightweight container engine which deserves a lightweight networking for containers, too. DaoliNet's NAT flow based connection between a pair of communications entities is a lightweight method to isolate overlay network. This lightweight network virtualization technique uses no packet encapsulation for tunnel construction. Packet encapsulation, e.g., VXLAN (aka "network hypervisor") used in Openstack Neutron, is too heavyweight for constructing overlay network for containers. Let's look at the case of firewall for an overlay network constructed from packet encapsulation. Now firewal-in-out must be at a so-called virtual tunnel endpoint (vtep) where packet encapsulation/decapsulation are performed. Such vtep point forms a traffic chokepoint. Since DaoliNet does not use packet encapsulation, firewall policy is simply a NAT flow which the Controller sees between a pair of communications requestor and responder. With OVS being ubiquitously distributed in every Docker server, firewall policy for individual containers are also distributed to every Docker host which hosts the containers. Such real-time flow configuration based firewall has no chokepoint.


**More in our website**: http://www.daolicloud.com/html/technology.html

**SlideShare** http://www.slideshare.net/daolinetppt/daolinet-lightweight-and-simple-networking-for-docker
