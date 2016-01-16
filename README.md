DaoliNet for Lightweight Docker Networking
=================

DaoliNet is a Software Defined Networking (SDN) system that is designed for lightweight network connections for Docker containers, with high availability, performance and scale-out.

Top-Level Features
------------------
* Lightweight connection of Docker containers, just like Docker's lightweight virtualization of containers without the extra load of a hypervisor, means you can get more out of your hardware resource.

* Connected containers can be distributed over a swarm of Docker hosts anywhere, which are a mixture of laptops or PCs in your office or home, virtual machines or servers in your own datacenter, or public clouds such as AWS.

* High avalability replication of micro-servicing containers are streamline provisioned to suit the dynamic nature of containers.

**More in our website**:  http://www.daolicloud.com
 

![](http://www.daolicloud.com/dashboard/static/github/topology.png)

**Figure 1, DaoliNet Topology**


Docker in Need of Lightweight Networking
=================

Docker is awesome! It is a container engine to virtualize server CPUs much more efficient than a hypervisor does for virtual machines (VMs). A Docker host can partition an X86 server into thousands of containers. Containers are playing more and more roles in cloud computing in place of VMs. However, because each Docker host is created independently from one another, containers in different Docker hosts are by default not connected one another. We need an efficient and lightweight networking solution to connect containers which are distributed in multiple Docker hosts.

Existing Solutions
------------------
There exists a number of offers for Docker networking: Weave, Flannel, and Colico are well-known open source projects for Docker networking. Calico and Weave, require that each Docker host must provide the full function of a router to perform route discovery and state update with other Docker hosts as routers; this is unfortunately very heaviweight in resource utilization. Flannel requires that Docker hosts run packet encapsulation, e.g., VXLAN, to tunnel container packets in-between different Docker hosts; packet encapsulation not only consumes extra load of hardware resource (VXLAN is also known as "network hypervisor"), but also nullifies useful network diagnosing tools such as traceroute. It is a fact that networking is a core feature of Docker that is relatively immature and still under heavy development.

How DaoliNet Works
==================

DaoliNet Network Virtualization
-------------------------------
The DaoliNet Network Virtualization is based on OpenFlow Standard, which completely separates the control and forward planes for your virtualized cloud network. With DaoliNet, Docker hosts are created and managed independently; there is no deed for them to know one another. This greatly simplifies the management and scalability of Docker cloud. Below let us provide an introduction to important advantages enabled by OpenFlow.

OpenFlow Controller
-------------------
An OpenFlow Controller (below we use the Controller for OpenFlow Controller) is a set of distributed web-service-like agents. It receives a "PacketIn" request from a Decker host and replies a "PacketOut" response to the requesting host. A packetin request is a normal network packet that a Docker host receives from a container but does not know how to process switching/routing/gateway-forwarding/firewall-filtering, due to lack of configuration intelligence. A packetout response from the Controller is a flow which configures in real time a Docker host to turn it into intelligent for forwarding packets.

Servers are Network Devices
---------------------------
DaoliNet uses standard X86 servers running Linux kernel with Open-v-Switch (OVS) as network devices. When joining a cloud resource pool, a server has no any network configuration information apart from only knowing the IP addresses of the OpenFlow Controllers. This means that the Docker hosts joining a cloud resource pool are completely independent of one another, having no whatever knowledge of one another at all. Once real-time configured by the Controller, a Docker host becomes intelligent to forward packets in various network functions, e.g., switching (L2), routing (L3) and gateway (L4: NAT-in-out, and Firewall), and can also form security groups for a cloud tenant, and handle load balance at the edge of a cloud network.

Overlay Network for Distributed Containers
------
When a container is created in a Docker host server, its network medadata will be captured by DaoliNet OpenFlow Controller (below we use the Controller for short). The network metadata include: the container's MAC address, the container's IP address, the server's intranet MAC, the server's intranet IP, and the default gateway IP (the default gateway is the server). The Controller will also capture the security group information of the container, i.e., information about a group of containers belonging to one security group, which is specified by the owner of the containers.

When a container (say C1 in Figure 2 below) initiates a communication session to another container (C2), packets from C1 are received by the Docker host (Server1) for to forward to C2 (hosted by Server2). However, Server1 has no switching, routing, or gateway information for these packets. In OpenFlow standard, the OVS in Server1 will ask for help from the Controller by lifting the first packet to the Controller. This packet-lift-to-controller event is called packetin (see PacketIn1 in the figure below).
 

![](http://www.daolicloud.com/dashboard/static/github/workflow.png)

**Figure 2, NAT-NAT Flow**


The packetin to the Controller contains network metadata which suffice the Controller to judge whether or not two containers are allowed to communicate. The metadata include: src-MAC and src-IP of C1, dst-MAC and dst-IP of C2, plus those of Server1 and Server2. Suppose that the Controller judges from security group policy that C1 and C2 are allowed to communicate, it will respond to Server1 with packeout (PacketOut1), which is a flow sent to Server1 to real-time configure the server. In addition, the Controller will also send a corresponding flow to Server2 as a real-time configuration (PacketOut2). Upon receipt the respective flows by Server1 and Server2, the OVS-es in these Docker hosts become knowing how to forward the packets, and the Controller will not be contacted any more for the remainder communications session.

The above pair of flows uniquely define a session of connection between C1 and C2 irrespective of their locations. Let's analyze the following two cases:

**Case 1: C1 and C2 are in the same Docker host**

In this case, Server1 = Server2. There are two sub-cases. Sub-case 1: the IP addresses of C1 and C2 are in the same subnet. Then the flow packetout to the Docker Server is MAC address defined, i.e., a switching flow, very simple! Notice that if Controller judges from the security group policy that C1 and C2 are not allowed to communicate, then it will not packetout a mac flow to the Docker Server, and thereby C1 and C2 will not be able to communicate even though they are in the same Docker Server. Sub-case 2: The IP addresses of C1 and C2 are in different subnets. Then the flow packetout to the Docker server is not only MAC defined, but also IP address defined, i.e., also a routing flow. In this case, the ovs linking the two containers also playing the role of a router.

**Case 2: C1 and C2 are in different Docker hosts**

In this case, Server1 =\= Server2. Two flows will be packetout to Server1 and Server2, respectively. The flow for Server1 is NAT-out, and that for Server2 is NAT-in. Notice that both NAT flows are identified by the src-PORT of the communications initiator, i.e., C1 in Figure 2. This src-PORT of C1 is a random number created by C1. With these two flows, C1 and C2 are connected. With NAT flows, the packets traveling between the two Docker servers use the underlay IP addresses of the two servers, and the packets traveling between a container and its hosting server use overlay IP address of the container, respectively.

OVS Forms Distributed Routers
---
We notice that there is no need for the IP addresses of C1 and C2 to be in the same subnet. In the case of C1, C2 belonging to different subnets, the OVS-es form distributed, ubiquitous and virtualized routers in every Docker host.

OVS Forms Distributed Gateways
---
NAT-out from a container to a node in the Internet, and Firewall-ingress from an Internet node to a container can also be hotplug established by the Controller as real-time packetout NAT flows. Such a NAT flow is also identified by src-PORT of a communications initiator. The distributed gateways are reflected in Figure 1 as the Internet connections for each Docker host server.

Lightweight Network Virtualization, No Packet Encapsulation
---
We know that an overlay network can be constructed using packet encapsulation. For example, OpenStack Neutron uses VXLAN (aka "network hypervisor") to encapsulate VM packets and form isolated overlay networks. Packet encapsulation uses a header tag to uniquely identify an isolated overlay network, e.g., the header tag for VXLAN is called Virtual Network Identity (VNI). However, as the nick name "network hypervisor" suggests, Packet encapsulation would be too heavyweight for constructing overlay networks for containers.

Docker is a lightweight container engine and deserves an also lightweight networking solution for connecting containers. From our descriptions on DaoliNet networking solution, we can see that an overlay network for distributed containers are pair-wise connected by the Controller issuing a pair of NAT-out, NAT-in flows. This pair of NAT flows are uniquely identified by the src-PORT of a communications initiator; the Controller can maintain the uniqueness of src-PORT in the lifetime of a connection. This unique src-PORT number plays the exact role of an encapsulation header tag to identify and isolate the overlay network, however, without resorting to packet encapsulation. Thus, DaoliNet is a lightweight networking solution suitable for connecting Docker containers.

No Firewall Chokepoint
---
If an overlay network is constructed using packet encapsulation, then firewal-in-out must be at a so-called virtual tunnel endpoint (vtep) where packet encapsulation (for firewall ingress direction), and packet decapsulation (for firewall egress direction), are processed. Obviously, such a vtep point forms a traffic chokepoint. Since DaoliNet does not use packet encapsulation, firewall policy is simply a NAT flow (NAT-in flow for firewall ingress direction, NAT-out flow for firewall egress direction) which is packetout provided by the Controller upon seeing connection request between a pair of communications initiator and responder. With OVS being ubiquitously distributed in every Docker host server, firewall policy for every individual container is also ubiquitously distributed to every Docker host server which hosts the container. Such distributed firewall has no chokepoint. That is why we have drawn in Figure 1 for every Docker host server to have a direct connection to the Internet.

Seamless Connecting Virtual Machines and Containers
---
With DaoliNet, OVSes under OpenFlow Controllers form distributed switches, routers, gateways and firewalls, the DaoliNet technology obviously also works for connecting virtual machines (VMs) running on hypervisors (also connecting VMs and containers) as long as OVSes are also used with hypervisors. The reader can view that some of the Linux servers in Figures 1 and 2 are replaced with hypervisors, and that containers are replaced with VMs. DaoliNet connecting VMs, containers, and between VMs and containers use exactly the same technique. Seamless and streamline connecting VMs and containers is the unique feature from DaoliNet.


**More in our website:** http://www.daolicloud.com/html/technology.html

**SlideShare:** http://www.slideshare.net/daolinetppt/daolinet-lightweight-and-simple-networking-for-docker
