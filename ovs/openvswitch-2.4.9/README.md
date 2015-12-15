Openvswitch Extension Work by DaoliNet
=================================

Why Extension?
---------------------------------

DaoliNet network virtualization solution uses openvswitch (OVS). However, the current version of OVS does not support the ping feature in ICMP. Our extension work adds the ping feature to OVS.

If you want us to add other OVS features, please contact us: daolinet@gmail.com, or daolinet@daolicloud.com

Source code containing DaoliNet's work is commented with //add by daolicloud

=================================

How to compile and install
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


[USE]

Example

	ovs-ofctl add-flow br-int dl_type=0x800,nw_proto=1,icmp_identify=xxxx,\
					actions=mod_icmp_identify:xxxx,output:xxx

==================================
CONTACT US
----------------------------------
daolinet@daolicloud.com
