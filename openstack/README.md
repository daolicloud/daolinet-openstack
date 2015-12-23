Installation：
===============================================================
Install OpenStack:
------------------
RDO Quickstart:
Deploying RDO is a quick and easy process if your system is CentOS.

        https://www.rdoproject.org/install/quickstart/

Other Ways:
Please visit OpenStack website:
        % http://www.openstack.org/docs

Note: The current version release is "Libery".


Download the daolinet sources from github:
------------------------------------------
	% git clone https://github.com/daolicloud/daolinet/

Download the openstack nova-docker from github:
-----------------------------------------------
        % git clone https://git hub.com/openstack/nova-docker.git
        % cd nova-docker/
        % python setup.py install

Run Scripts:
-----------------
	Controlle Node:
 		% cd openstack/scripts/
		% ./controller.sh

	Compute Node:
 		% cd openstack/scripts/
		% ./compute.sh

Install Controller:
-------------------
	% cd ryu/
	% python setup.py install

	% cd ../daolicontroller
	% python setup.py install
	% systemctl start daolicontroller

Install Openvswitch:
--------------------
        You can run:
        ============  
               %  ./boot.sh
               %  ./configure --with-linux=/lib/modules/`uname -r`/build --prefix=/usr --localstatedir=/var
               %  make
               %  make install
               %  make modules_install
               %  /sbin/modprobe openvswitch
               %  mkdir -p /usr/local/etc/openvswitch
               %  ovsdb-tool create /usr/local/etc/openvswitch/conf.db vswitchd/vswitch.ovsschema
               %  ovsdb-server --remote=punix:/usr/local/var/run/openvswitch/db.sock \
                                      --remote=db:Open_vSwitch,Open_vSwitch,manager_options \
                                      --private-key=db:Open_vSwitch,SSL,private_key \
                                      --certificate=db:Open_vSwitch,SSL,certificate \
                                      --bootstrap-ca-cert=db:Open_vSwitch,SSL,ca_cert \
                                      --pidfile --detach
               %  ovs-vsctl --no-wait init
               %  ovs-vswitchd --pidfile --detach
        or run:
        ======
               % bash ./setup.sh

        Edit daolienv file:
        ==================
              % PRV_DEV= "Private Interface Name"
              % PUB_DEV= "Public Interface Name" #(The device name same with PRV_DEV.)
              % DB_HOST= "Host of database"
              % DB_PWD=  "Password of database"

	%  ./run
	% ovs-vsctl set-controller br-int tcp:<ControllerAddress>:6633


Download Docker Image:
----------------------
	Download testing image from docker repositries.
	% docker pull daolicloud/centos6.6-ssh
        % . ./keystonerc_admin
        % docker save daolicloud/centos6.6-ssh | docker image-create --name daolicloud/centos6.6-ssh --disk-format raw --controller-format docker --visibility public
