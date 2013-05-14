#!/bin/sh

vmx_op_cmd="./vmx-op.py"

"vmx_op [ -i <vmx_file_0> -i <vmx_file_1> ] [ -e 'vmx_op_expr' -e ... ] -o output_file"

" (-i -) or no -i is stdin, (-o -) or no -i is stdout"

"files and expressions are evaluated in order"





vmx_op () {

	cat /dev/null > _.vmx

	{ 	while (( "$#" )); do

			if [ "${1#-}" = "e" ]; then
				shift
				echo "$1"
				shift
				continue
			fi

			if [ "${1#-}" = "i" ]; then
				shift
					if [ "$1" = "-" ]; then
				 		cat -
				 	else
				 		cat "$1"
				 	fi
				shift
				continue
			fi

			if [ "${1#-}" = "o" ]; then
				shift
				[ "$1" = "-" ] || vmx_op_cmd="$vmx_op_cmd > $1"
				shift
				continue
			fi

			if [ "$1" = "-" ]; then
				cat -
				shift
				continue
			fi
			
			if [ -f "$1" ]; then
				cat $1
				shift
				continue
			fi

			shift
		done
		cat -
	} | $vmx_op_cmd > outfile

}

vmx_get() {

	key=$1
	vmx_file=$2
	[ -z $vmx_file ] && vmx_file='_.vmx'

	{ cat $vmx_file; echo $key; } | $vmx_op_cmd

}



vmx_change() {

	stmt=$1
	vmx_file=$2
	[ -z $vmx_file ] && vmx_file='_.vmx'

	{ cat $vmx_file; echo $stmt; } | $vmx_op_cmd > $vmx_file

}

