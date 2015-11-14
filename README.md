What is DaoliNet?
=================

DaoliNet is a Software Defined Networking (SDN) system that is designed to achieve lightweight network connections for Docker containers, with high availability, performance and scale-out.

Top-Level Features
------------------

* Namespace-based lightweight partition of the physical network resource on X86 servers, just like Docker's lightweight namespace partition for the CPU resource on X86 servers.

* That Docker containers are connected to form VPCs (Virtual Private Clouds) and security groups takes place in user space without any server configurations. Thus scale-out distribution of Docker servers has a plug-and-play "for dummies" simplicity.

* VPCs and security groups are strictly isolated one another without server hosts being pre-configured for, e.g., VLAN, VXLAN, GRE, iptables, etc., settings. This unique feature of DaoliNet not only greatly saves server CPUs, just like Docker saving server CPUs by avoiding hypervisors, but also more importantly: since servers are network-knowledge-less, containers forming a VPC are freely and dynamically distributed to scale-out span over different servers, datacenters, or even behind different firewalls, irrespective of their location.

* Pure software implementation, completely distributed over any underlying physical network, high avalability by plug-and-play adding redundant and network-knowledge-less servers.


**Checkout our website**:  http://www.daolicloud.com

![DaoliNet Topology](http://www.daolicloud.com/static/topology.png)

Docker in Need of Efficient Networking
=========================

Docker is awesome! It simplifies provisioning micro-servicing containers to virtualize CPUs much more efficient and lightweight than virtual machines (VMs). Containers are playing more and more roles in cloud computing and bigdata processing in places of VMs. However, there is one thing yet in need: an also simplified, efficient and lightweight networking solution which can easily connect containers in distribution across different Docker hosts.

What Problem Docker Networking has
----------------------------------

A Docker host can partition thousands of micro-servicing containers. A Docker cloud or a bigdata project should ideally used a set of centrally managed containers which are from arbitrarily distributed number of Docker hosts. Containers which are contributed from one host to the project should be networking isolated from the rest the containers in the host, and containers which are contributed from different hosts to the project should be networking connected one another.

A Docker host provides essencially two non-trivial modes to networking its containers to connecting the world outside the host: (1) a flat network of host and containers being in one IP subnet, and (2) a NAT (Network Address Translation) network which the containers in a host are in an internal IP subnet and the host has an external IP address which will NAT communications for the containers within it. Mode (1) is obviously non-practical: you cannot imagine your home computers and smart phones having their IP addresses exposed to the Internet as your home router! Mode (2) is on the contrary very practical as home/office routers and base stations working today to form a well organized and extremely large scale Internet!

NAT is very kindly to an inside device to initiate communications, outgong packets are easily going out and the response packets allowed to enter. However, NAT will block packets initiated from outside the NAT gateway unless some pre-configurations are in place which is in fact a firewall policy. Now we see the problem in Docker's practical networking mode: two containers in different Docker hosts are not connected since one of them will NAT block packets which are initiated from the other.

Existing Solutions
------------------

There exists a number of offers for the Docker networking problem. Omitting these for Mode (1) which is obviously non-practical as we mentioned above, Weave is among those working for Mode (2) and is therefore meaningful for a description. Weave uses the packets encapsulation techniques in Open-V-Switch (OVS) such as VXLAN to tunnel in between two Docker hosts.

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

The DaoliNet uses standard X86 servers running Linux kernel with Open-v-Switch (OVS) agents as networking forwarding devices. When joining a cloud resource pool, a server has no any networking confirguration apart from only knowing the IP addresses of Openflow Controllers. This means that the servers joining a cloud resource pool are completely independent of one another, having no whatever knowledge of one another at all. Once on-the-fly configured by the Controller, a server becomes intelligent to forward packets in various network functions, e.g., switching (L2), routing (L3) and gateway-ing (L4: NAT-in-out, Firewall-in-out), and can also form security groups for a cloud tenant, and handle load balancing at the edge of a cloud network.

Distributed Containers Forming Overlay Network
------

When a container is created in a server, its network medadata are captured by DaoliNet Openflow Controller (below we use the Controller for short). The network metadata include: the container's MAC address, the container's IP address (assigned to by the Controller as the DHCP server), the server's intranet MAC, the server's intranet IP, and the default gateway IP (the default gateway is the server). The Controller also capture the security group information of the container, i.e., information about a group of containers belonging to one security group, which is specified by the owner of the containers.

When a container (say C1 in the figure below) initiates a communication to another container (C2), the first packet is an ARP one. In DaoliNet, the ARP packet will not be broadcast, instead it will be unicast to the Controller. The Controller has information to answer this ARP (the MAC of C2), again, unicast back to the ARP origin container. Then the container will send out communication packets. Since the server's OVS has no switching, routing, gatewaying information for these packets, a packetin event, sending the packet to the Controller, will occur

![Workflow](http://www.daolicloud.com/static/workflow.png)

