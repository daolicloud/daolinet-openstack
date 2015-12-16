#!/bin/bash

NOVA_CONF=$(crudini --get /etc/nova/nova.conf DEFAULT sql_connection)
KEYSTONE_CONF=$(crudini --get /etc/keystone/keystone.conf database connection)

if [ -z "$SQL_CONF" -o -z "$KEYSTONE_CONF"]; then
   echo "Check /etc/nova/nova.conf and /etc/keystone/keystone.conf"
   exit 1
fi

NSQL_CLI=$(echo $NOVA_CONF | sed 's/@[^\/]*//' | awk -F[:/] '{printf "%s -u%s -p%s %s ",$1,$4,$5,$6}')
KSQL_CLI=$(echo $KEYSTONE_CONF | sed 's/@[^\/]*//' | awk -F[:/] '{printf "%s -u%s -p%s %s -e ",$1,$4,$5,$6}')

yum remove openstack-neutron openstack-neutron-ml2 python-neutron openstack-neutron-openvswitch openstack-neutron-common openvswitch
rm -rf /etc/neutron/ /var/lib/neutron/
$KSQL_CLI "delete from endpoint where service_id in (select id from service where type='network');delete from service where type='network';";

rm -rf /usr/lib/python2.7/site-packages/keystoneclient
cp -r ../keystoneclient/ /usr/lib/python2.7/site-packages/
rm -rf /usr/lib/python2.7/site-packages/novaclient
cp -r ../novaclient/ /usr/lib/python2.7/site-packages/
rm -rf /usr/lib/python2.7/site-packages/nova
cp -r ../nova/ /usr/lib/python2.7/site-packages/
rm -rf /usr/share/openstack-dashboard
cp -r ../openstack-dashboard/ /usr/share/

admin_token=$(crudini --get /etc/keystone/keystone.conf DEFAULT admin_token)
local_settings="/usr/share/openstack-dashboard/openstack_dashboard/local/local_settings.py"
cp /etc/openstack-dashboard/local_settings $local_settings
if [ -z "$(cat $local_settings | grep ADMIN_TOKEN)" ]; then
  echo "ADMIN_TOKEN=$admin_token" >> $local_settings
fi

rpm -q docker || yum install -y docker
rpm -q docker-python || yum install -y docker-python
openstack-config --set /etc/nova/nova.conf DEFAULT compute_driver novadocker.virt.docker.DockerDriver
openstack-config --set /etc/nova/nova.conf DEFAULT firewall_driver nova.virt.firewall.NoopFirewallDriver
openstack-config --set /etc/nova/nova.conf DEFAULT compute_manager nova.daolicloud.compute_manager.ComputeManager
openstack-config --set /etc/nova/nova.conf DEFAULT network_manager nova.daolicloud.network_manager.SimpleManager
openstack-config --set /etc/nova/nova.conf DEFAULT network_api_class nova.network.api.API
openstack-config --set /etc/nova/nova.conf DEFAULT security_group_api nova
openstack-config --set /etc/glance/glance-api.conf DEFAULT container_formats ami,ari,aki,bare,ovf,ova,docker
openstack-config --set /usr/lib/systemd/system/openstack-nova-compute.service Service User root

setenforce 0
sed -i 's/^SELINUX=.*/SELINUX=disabled/' /etc/sysconfig/selinux

$NSQL_CLI -e "alter table fixed_ips drop index uniq_fixed_ips0address0deleted;delete from fixed_ips; delete from networks;insert into networks(created_at,injected,cidr,netmask,bridge,gateway,broadcast,dns1,label,multi_host,uuid,deleted,enable_dhcp,share_address) values(NOW(),0,'10.0.0.0/8','255.0.0.0','br-int','10.255.255.254','10.255.255.255','8.8.8.8','novanetwork',0,'$(uuidgen)',0,0,0),(NOW(),0,'172.16.0.0/12','255.240.0.0','br-int','172.16.255.254','172.31.255.255','8.8.8.8','novanetwork',0,'$(uuidgen)',0,0,0),(NOW(),0,'192.168.0.0/16','255.255.0.0','br-int','192.168.255.254','192.168.255.255','8.8.8.8','novanetwork',0,'$(uuidgen)',0,0,0)"
$NSQL_CLI < db.sql

systemctl daemon-reload
systemctl enable docker.service
systemctl start docker.service
systemctl restart openstack-nova-api
systemctl restart openstack-nova-network
systemctl restart openstack-nova-conductor
systemctl restart openstack-nova-compute
systemctl restart openstack-glance-api

echo "Installation Successfully"
