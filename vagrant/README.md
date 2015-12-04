Quick Start
===========

Prerequisites:
--------------
On the host, equivalent or greater: 
* VirtualBox 4.3.32 or greater
* Vagrant 1.7.4

Installation:
-------------
Before install the Virtualbox, these tools are necessary:

    % sudo yum install -y kernel-devel kernel-headers kernel gcc

Reboot your machine:

    % sudo reboot

Get the public-yum repo file of Virtualbox:

    % wget -P /etc/yum.repos.d http://download.virtualbox.org/virtualbox/rpm/{distro}/virtualbox.repo
  
Replace {distro} with your Linux distribution (eg: el for CentOS, rhel for Red Hat, fedora for Fedora).


Install the Virtualbox:
e.g. $ sudo yum install -y VirtualBox-5.0.x86_64


Install the Vagrant:
e.g. $ sudo rpm -ivh https://releases.hashicorp.com/vagrant/1.7.4/vagrant_1.7.4_x86_64.rpm


Running:
--------
In current directory.

    % vagrant up
    % ./pre.sh
    % vagrant ssh

Visit our system by 10.10.10.10.

Delete：
-------
In current directory. 

    % vagrant destroy
