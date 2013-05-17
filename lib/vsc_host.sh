#!/bin/sh
#this is for installing ssh key on the ESXi server
#which is a bit different from a normal linux box


# vsc_remote_init_esxi () {
# 	cat ~/.ssh/id_rsa.pub | ssh ${1} 'cat >> /etc/ssh/keys-root/authorized_keys'
# }

# vsc_remote_init_linux () {
# 	cat ~/.ssh/id_rsa.pub | ssh ${1} 'cat >> /etc/ssh/keys-root/authorized_keys'
# }

# vsc_remote_init_core () {

# 	for host in hypervisor dns_server dhcp_server ; do
		
# 		[ "${host}.os" = 'ESXi' ] && vsc_remote_init_esxi "root@$( g ${host}.name )"
# 		[ "${host}.os" = 'linux'] && vsc_remote_init_linux "root@$( g ${host}.name )"

# 	done

# }

# vsc_remote_test () {

# 	for host in hypervisor dns_server dhcp_server ; do
		
# 		vsc_remote "$host" "echo $host" 

# 	done

# }

# vsc_remote () {
	
# 	host=$1
# 	shift

# 	ssh root@${1} "$@" 

# }

vsc_host_info() {

	host_id=$1

	load ".id=${host_id}"



	for host in $( vmx_db_list hosts )
	do

} 

vsc_host_remote_test() {
	host_id=$1
	load_record host $host_id
	ssh ${host_user}@${host_name} 'echo hi' 
}

vsc_host_remote_call() {
	$host_id=$1
	shift
	[ "$1" = '.'] && func=$CMD || func=$1
	cat | $_vmx_op | ssh $( vsc_host_user $1 )@$( vsc_host_name $1 ) $func
}

vsc_host_remote_init() {

	host_id=$1

	load_record host $host_id

	cat ~/.ssh/id_rsa.pub | ssh ${1} 'cat >> /etc/ssh/keys-root/authorized_keys'
}
# /client/vm/vmx

#% hosts = client
vsc_vm_vmx() {
	vsc_remote hypervisor .
}


# /hypervisor/vm/vmx

#% hosts=hypervisor
#% hypervisor.type=esx
vsc_vm_vmx() {
	receive
	vmx_path="${datastore}/${name}/${name}.vmx"
	echo $vmx_path

	if ! [ -f "$vmx_path" ]; then 
		err='vmx file does not exist'
		send err
		return 1
	fi

	sendf "$vmx_path"
	return 0
}






