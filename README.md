What is DaoliNet?
=================

DaoliNet is a Software Defined Networking (SDN) system that is designed for lightweight network connections for Docker containers, with high availability, performance and scale-out.

Top-Level Features
------------------

* Namespace-based lightweight partition of the physical network resource on X86 servers, just like Docker's lightweight namespace partition for the CPU resource on X86 servers.

* That Docker containers are connected to form VPCs (Virtual Private Clouds) and security groups takes place in user space without any server configurations. Thus scale-out distribution of Docker servers has a plug-and-play "for dummies" simplicity.

* VPCs and security groups are strictly isolated one another without server hosts being pre-setup "networking hypervisors", e.g., VLAN, VXLAN, GRE, iptables, etc. This unique feature of DaoliNet not only greatly saves server CPUs, just like Docker saving server CPUs by avoiding hypervisors, but also more importantly: since servers are network-knowledge-less, containers forming a VPC are freely and dynamically distributed to scale-out span over different servers, datacenters, or even behind different firewalls, irrespective of their location.

* Pure software implementation, completely distributed over any underlying physical network, high avalability by plug-and-play adding redundant and network-knowledge-less servers.


**Checkout our website**:  http://www.daolicloud.com

![DaoliNet Topology](http://www.daolicloud.com/static/topology.png)

Docker in Need of Efficient Networking
=========================

Docker is awesome! It simplifies provisioning micro-servicing containers to virtualize CPUs much more efficient and lightweight than virtual machines (VMs). Containers are playing more and more roles in cloud computing and bigdata processing in places of VMs. However, there is one thing yet in need: an also simplified, efficient and lightweight networking solution which can easily connect containers in distribution across different Docker hosts.

A Docker host can partition thousands of micro-servicing containers. A Docker cloud or a bigdata project should ideally used a set of centrally managed containers which are from arbitrarily distributed number of Docker hosts. Containers which are contributed from one host to the project should be networking isolated from the rest the containers in the host, and containers which are contributed from different hosts to the project should be networking connected one another.

Docker provides essencially two non-trivial networking modes for the containers in a Docker host to connect the outside world: (1) linux bridge mode which is a flat network with the host and its containers being in one IP subnet, and (2) NAT (Network Address Translation) network mode which the containers in a host have an internal IP subnet and the host has an external IP address, and the containers communicate with the outside world via the host NAT using the external IP address of the host. Mode (1) is very difficult to manage network isolation and scalability. Mode (2) is quite practical since NAT is ubiquitously working everywhere in the Internet: routers in homes and offers, base stations, etc., all use NAT in the borders of intranets and the Internet.

NAT works very kindly to an intranet node initiating communications to an outside node: for all outgoing packets, NAT will maintain a stateful flow for responding packets to enter. However, NAT will by default block packets which are initiated from outside the NAT gateway unless some pre-configuration is in place which is in essense a firewall policy. Now we see a problem in Docker's practical networking mode: two containers in different Docker hosts are not connected since one NAT host will block packets from the other.

Existing Solutions
------------------

There exists a number of offers for the Docker networking problem. Weave and Flannel are among those working for Mode (2). Both uses encapsulation techniques for connecting containers which are distributed in two Docker hosts. For packets encapsulation to be applied to Docker networking, each Docker host is setup a Virtual Tunnel End Point (vtep) where cross host packets are encapsulated and decapsulated. These vteps work like a "networking hypervisor". They are considered to be heaviweight technologies and also complicate cloud management. For example, encapsulation will cause packet fragmentation/reassambly at two vteps due to encapsulation header expanding the packet size exceeding the maximum transmition unit (MTU). Docker's lightweight CPU virtualization is awesome exactly because it has avoided heavyweight CPU hypervisors, it should also avoid heavyweight "networking hypervisor"!

How DaoliNet Works
============

DaoliNet Network Virtualization
-------------------------------

The DaoliNet Network Virtualization is based on Openflow Standard, which completely separates the control and forward planes for your virtualized cloud network. Below let us provide an introduction to important advantages enabled by Openflow.

Openflow Controller
-------------------

This is a set of distributed web service agents. They receive a "PacketIn" request from a server host and reply a "PacketOut" response to the requesting server. A packetin request is a normal network packet that the server receives but does not know how to process switching/routing/gateway-in-out/firewall-in-out, due to lack of configuration intelligence. A packetout response from the Controller is a flow which on-the-fly configures the packetin server to turn it into intelligent for forwarding packets.

Servers as Networking Boxes: Distributed Switches, Routers, and Gateways
---------------------------

The DaoliNet uses standard X86 servers running Linux kernel with Open-v-Switch (OVS) as networking forwarding devices. When joining a cloud resource pool, a server has no any networking confirguration information apart from only knowing the IP addresses of Openflow Controllers. This means that the servers joining a cloud resource pool are completely independent of one another, having no whatever knowledge of one another at all. Once on-the-fly configured by the Controller, a server becomes intelligent to forward packets in various network functions, e.g., switching (L2), routing (L3) and gateway-ing (L4: NAT-in-out, Firewall-in-out), and can also form security groups for a cloud tenant, and handle load balancing at the edge of a cloud network.

Overlay Network for Distributed Containers
------

When a container is created in a Docker host server, its network medadata will be captured by DaoliNet Openflow Controller (below we use the Controller for short). The network metadata include: the container's MAC address, the container's IP address, the server's intranet MAC, the server's intranet IP, and the default gateway IP (the default gateway is the server). The Controller will also capture the security group information of the container, i.e., information about a group of containers belonging to one security group, which is specified by the owner of the containers.

When a container (say C1 in the figure below) initiates a communication session to another container (C2), packets from C1 are received by the Docker host (Server1) for to forward to C2 (hosted by Server2). However, Server1 has no switching, routing, or gatewaying information for these packets. In Openflow standard, the OVS in Server1 will ask for help from the Controller by lifting the first packet to the Controller. This packet-lift-to-controller event is called packetin (see PacketIn1 in the figure below).

![Workflow](http://www.daolicloud.com/static/workflow.png)

The packetin lifted to the Controller contains sufficient network metadata: source MAC and IP of C1, destination MAC and IP of C2, plus those of Server1 and Server2. Suppose that the Controller judges from security policy that C1 and C2 can legally communicate, it will respond to Server1 with packeout (PacketOut1), which is a flow sent to Server1 to on-the-fly configure the server. In addition, the Controller will also send a corresponding flow to Server2 as an on-the-fly configuration (PacketOut2). Upon receipt the respective flows by Server1 and Server2, the OVS-es in these two Docker hosts become knowing how to forward the packets, and the Controller will not be contacted any more for the remainder communication session.

The above pair of flows uniquely defines a session of connection between C1 and C2 irrespective of the locations of C1 and C2. Let's analyse the following two cases. Case 1: C1 and C2 being in the same Docker host (Server1 = Server2), the pair of flows are MAC defined. Case 2: C1 and C2 being in different Docker hosts (Server1 =\= Server2), the flow for Server1 is NAT-out, and that for Server2 is NAT-in, and both flows are identified by the src port number which is a randum number created by C1. We also notice that there is no need for C1 and C2 being in the same subnet, this is because the OVS-es form distributed and ubiquitous routers in every Docker host!

NAT-out from a container to a node in the Internet, and Firewall-ingress from an Internet node to a container can also be on-the-fly established by the Controller.
