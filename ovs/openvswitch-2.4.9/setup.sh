#!/bin/bash
./boot.sh

./configure --with-linux=/lib/modules/`uname -r`/build --prefix=/usr --localstatedir=/var

make

make install

make modules_install

/sbin/modprobe openvswitch

mkdir -p /usr/etc/openvswitch

ovsdb-tool create /usr/etc/openvswitch/conf.db vswitchd/vswitch.ovsschema

ovsdb-server --remote=punix:/var/run/openvswitch/db.sock \
                             --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
                             --private-key=db:Open_vSwitch,SSL,private_key \
                             --certificate=db:Open_vSwitch,SSL,certificate \
                             --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert \
                             --pidfile --detach

ovs-vsctl --no-wait init

ovs-vswitchd --pidfile --detach
