#!/bin/sh
#this is intended to be run from the ESX server console

log_err() {
	echo "$@" 1>&2
}

exit_err() {
	log_err("$@")
	log_err('exiting...')
	exit(1)
}

SrcVmName=${1}
DstVmName=${2}

root_path="/vmfs/volumes/${DEFAULT_VMFS_STORE}"
src_path="${root_path}/${SrcVmName}"
dst_path="${root_path}/${DstVmName}"
src_vmx="${SrcVmName}.vmx"
dst_vmx="${DstVmName}.vmx"
src_vmdk="${SrcVmName}.vmdk"
dst_vmdk="${DstVmName}.vmdk"

[ -d $src_path ]               || exit_err("source directory ${src_path} does not exist") 
[ -f "${src_path}/${src_vmx}"] || exit_err("src vmx file ${src_vmx} does not exist")
[ -d $dst_path ]               || exit_err("there is already a directory at ${dst_path}")

mkdir $dst_path 			   || exit_err("could not create directory at ${dst_path}")

vmx_op clone "${src_path}/${src_vmx}" "${dst_path}/${dst_vmx}" "${dst_path}/${ident_vmx}" || exit_err("unable to clone vmx file")

vmkfstools -i "${src_path}/${src_vmdk}" "${dst_path}/${dst_vmdk}" || exit_err("unable to copy clone vmdk file")

vim-cmd solo/registervm "${dst_path}/${dst_vmdk}" || exit_err("unable to register vm")


