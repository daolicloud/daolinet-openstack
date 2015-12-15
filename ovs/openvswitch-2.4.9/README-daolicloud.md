Open vswitch expand by daolilcoud
=================================
Why we want to expand ?
---------------------------------
Daolicloud is committed to providing cloud computing services enterprises.
We use openstack platform to provide services. We have our own network vir-
-tualization solution. We use openvswitch for our solution.But we found 
Open vswitch can not support some network protocols. So we have two development
of it.

=================================
Features ?
---------------------------------
At present it can deal with icmp request&reply packet like regular device when NAT.

=================================
How to use ?
---------------------------------
[INSTALL]
./boot.sh
./configure --with-linux=/lib/modules/`uname -r`/build --prefix=/usr --localstatedir=/var
make 
make install

make modules_install
/sbin/modprobe openvswitch

mkdir -p /usr/local/etc/openvswitch
ovsdb-tool create /usr/local/etc/openvswitch/conf.db vswitchd/vswitch.ovsschema

ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock \
                     --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
                     --private-key=db:Open_vSwitch,SSL,private_key \
                     --certificate=db:Open_vSwitch,SSL,certificate \
                     --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert \
                     --pidfile --detach

ovs-vsctl --no-wait init
ovs-vswitchd --pidfile --detach

ovs-vsctl add-br br0
ovs-vsctl add-port br0 eth0
----------------------------------
[USE]
Example
	ovs-ofctl add-flow br-int dl_type=0x800,nw_proto=1,icmp_identify=xxxx,\
					actions=mod_icmp_identify:xxxx,output:xxx

==================================
CONTACT US
----------------------------------
nvi@daolicloud.com
