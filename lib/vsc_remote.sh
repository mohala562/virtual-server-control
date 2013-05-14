#!/bin/sh
#this is for installing ssh key on the ESXi server
#which is a bit different from a normal linux box


vsc_remote_init_esxi () {
	cat ~/.ssh/id_rsa.pub | ssh ${1} 'cat >> /etc/ssh/keys-root/authorized_keys'
}

vsc_remote_init_linux () {
	cat ~/.ssh/id_rsa.pub | ssh ${1} 'cat >> /etc/ssh/keys-root/authorized_keys'
}

vsc_remote_init_core () {

	for host in hypervisor dns_server dhcp_server ; do
		
		[ "${host}.os" = 'ESXi' ] && vsc_remote_init_esxi "root@$( g ${host}.name )"
		[ "${host}.os" = 'linux'] && vsc_remote_init_linux "root@$( g ${host}.name )"

	done

}

vsc_remote_test () {

	for host in hypervisor dns_server dhcp_server ; do
		
		vsc_remote "$host" "echo $host" 

	done

}

vsc_remote () {
	
	host=$1
	shift

	ssh root@${1} "$@" 

}










