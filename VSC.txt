VSC API DOC
===========

Overview
--------

VSC is intended to ease deployment of virtual machines and

VSC is a tool to aid in the development of server software using virtualization.  Similar in concept to the Vagrant project, but using server virtualization, instead of desktop.  VSC provides a templating system for ESX5 which allows you to deploy standard VMs that are needed in multiple projects.   

Key Features
============

* Templating Interface using ESXi cmd api
* Integrate with DNS server so that deployed vms are automatically given a domain name
* Repos are mapped from shared storage to the virtual servers in virtual machines
*  
* Automatically map git repos into vm
* code repos can be edited locally with NFS mapping

* Code repos are stored on a shared nfs export, so they can be mounted into virtual machines and mapped to a webservers virtual server.
* Recognizes the concept of virtual machines and virtual server.  You can have multiples virtual server on one vm, or only one.
* DNS is integrated with virtual machines and virtual servers.  When you deploy a vm from a template DNS can be automatically configured on the network.
* Virtual Servers each get mapped to a dns name also


An Example for Spree:

Create a generic template for a linux server:

Say you create a ESX VM in Vsphere and install CentOS, install VM tools, update, configure a basic setup and call it CentOS6. now create a template from this VM.
Now shutdown the VM and run:

`vsc template create CentOS`

vsc has remote access configured so commands are run from your local machine. 

this creates a generic template for CentOS that you use to deploy a VM which works with vsc.

to deploy the template do:

`vsc template deploy CentOS WebServer`

this deploys a VM and sets it up to integrate with vsc.
    



This creates a template for this CentOS box







For instance say you want to test out a webserver application.  First you would deploy a  

VSC has both the concept of "Virtual Machines" and "Virtual Servers"


Virtual Machine Operations
--------------------------
### vsc vm ...

Manipulate configuration and runtime of **virtual machine** (guests) on a hypervisor.  This is not meant to replace the vendor specific ui for configuring/running vms but rather to extent and customize functionality and wrap certain command-line functionaliy, ie templates.

#### commands:

`vm < vm >`

**enter virtual machine context.**  Sets the working virtual machine and scopes future calls to `vsc vm` to <vm_name>.

`vm template create < vm > <template_name>`

**create a template from a vm**  Modifies vm with name <vm> so that it can be used as a template.  You can then deploy the template using `vm template deploy`

`vm template deploy <template> <new_vm_name> <config_file>`

**deploy a vm using a template vm**  A new vm <dst_vm_name> is initialized, virtual disk storage is cloned and a vm configuration is created by applying <config_file> to <template_name>    

`vm clone <src_vm> <new_vm_name>`

*make a duplicate of a virtual machine*  Like template deploy but no custom configuration of the destination vm takes place.  A new name and and machined ids are applied to the clone, any other configuration must be manually applied.  The cloned vm's virtual adapters are disconnected from the virtual switch so that no network address conflicts occur, you will need to boot into the vm and make changes before reconnecting the vm to the virtual switch.

`vm list`

**list vms on command-line**

`vm list templates`

**list templates on esx host which are templates**

`vm <vm> info`

**show info on a vm** including tempate info (what templates it is the base for, from what template it was deployed) and what virtual servers it is running

`vm <vm> ctrl <operation>`

**control vm state* Operations are:

* **status** (show vm state)
* **start** (power on vm )
* **stop** (power off a vm , this is a *hard* power off)
* **shutdown** (cleanly shutdown vm, using vmware tools to signal vm)
* **reboot** (cleanly resets the vm)

`vm <vm> request-mac-addr`

*request a network macaddr and set it on vnic*  This is for a static dhcp configuration, which is typically what you should be using for a server-type virtual-machine, since you desire a static ip but don't want to have to configure network ids on a deployed vm.  Requests a valid macaddr the dhcp server, the dhcp server sets up the new mac/ip pair in it's table returns this info to vsc.  Then vsc configures the mac addr on the vm's virtual network adaptor.

`vm <vm> set-domain-name <host_level_dns_prefix>`

*this configures the machine level hostname*  Sets the host level domain name.  When virtual servers are configured on a vm the are a prefix to this name.

`vm <vm> vmx-op <options>`

*use the vmx-op utility on the vm the*  See the vmx-op documentation.


Virtual Server Operations
-------------------------

###vsc server ...

Manipulate configuration and runtime of **server applications provided by virtual/physical hosts**. Many server daemons have the concept of virtual servers/ virtual hosts esp. webservers., after this 'server' means 'virtual server or server'.  In this specification each server is mapped to a dns entry. One important concept is that configuration and data (i.e repos)  can be located on a network/shared storage and mapped into hosts, there by allowing file editing etc. to occur from a local mapped drive.

#### config defaults:

#### commands:

`server create <domain_name> <options>`

*create a virtual server.* Creates a dns entry <domain_name> for the virtual server.  Configures virtual server based on options.  Creates a repo for the virtual server.

`server set_domain_name <old_domain_name> <new_domain_name>`

*change dns info for virtual server.* Change the local name and update the DNS server with <new_domain_name> preserves repo association.

`server <server_name> ctrl <operation>`
	
**control the virtual server runtime** 

operations are:
* enable
* disable
* reload

`server master ctrl <operation>`

**control the parent daemon for the server** In the case of multiple virtual servers this controls the parent process and affects all virtual servers.

operations are:
* status
* start
* stop
* restart

####file structure for servers

local storage:

/vsc
	/servers
		/<vs0> -> ../.repos/repo[1].uuid
		/<vs1> -> ../.repos/repo[0].uuid
	/.repos
		/repo[0].uuid
			<repo[0] contents>
		/repo.uuid[1]
			<repo[1] contents>

network storage:

/vsc
	/vms
		/<vm[0]>
			/<vs[0]
			/<vs[1]
		/<vm[1]>
			/<vs[2]>
	/servers
		/<vs[0]>.<vm[0]> -> ../.repos/repo[2].uuid
		/<vs[1]>.<vm[0]> -> ../.repos/repo[1].uuid
		/<vs[2]>.<vm[1]> -> ../.repos/repo[0].uuid
	/.repos
		/repo[0].uuid
		/repo[1].uuid
		/repo[2].uuid


##### example option defaults:

server.type = nginx.virtual
server.nginx.virtual.init = rails
server.start_on_create = true
repo.type = git
repo.git.clone_on_create = true

##### example options:

repo.url = https://github.com/spree/spree

##### example command

`vsc server create spree.web1.ginlane.local repo.url=https://github.com/spree/spree`

Remote Environment
==================

`vsc init ...`

`vsc remote test`

** test the remote connections **

`vsc remote init`

** distribute private keys to hosts in the environment ** this is necessary for passwordless authentication.  keys are distributed to all servers associated with vsc (hypervisor,dns_server,dhcp_server)

##### configuration options

remote.cmd = 'ssh'


Defaults and Config
===================


/.vsc
	conf

hypervisor_host_name = serve_the_net
hypervisor_type = ESXi
hypervisor_version = 5

repo.git.clone_on_create = true

dns_server_host_name = netutil
dns_server_type = dns-masq

dhcp_server_host_name = netutil
dhcp_server_type = dns-masq

dns_domain_suffix = ginlane.local

server_mount = fileserver://vsc

repo.type = git
repo.git.clone_on_create = true

server.type = nginx

fileserver://vsc
	vsc.conf


A Full Example
==============


#### example default global configuration:

hypervisor_host_name = serve_the_net
hypervisor_type = ESXi
hypervisor_version = 5

dns_server_host_name = netutil
dns_server_type = dns-masq

dhcp_server_host_name = netutil
dhcp_server_type = dns-masq
dns_domain = ginlane.local

server.type = nginx
server.nginx.init = rails
server.start_on_create = true

repo.type = git
repo.git.clone_on_create = true














