#!/bin/sh
# wrappers for vmx_op.py

_vmx_op="./lib/vmx_op.py"

#help_msg="vmx_op [ -i <vmx_file_0> -i <vmx_file_1> ] [ -e 'vmx_op_expr' -e ... ] > output_file"

vmx_op () {

	cmd=$_vmx_op

	{ 	if [ -z "$1" ]; then
			cat
			echo
		else
			while (( "$#" )); do

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
					 	echo
					shift
					continue
				fi

				if [ "$1" = "-" ]; then
					cat -
					shift
					continue
				fi
				
				if [ "$1" = "," ]; then
					echo
					shift
					continue
				fi

				echo -n "$1"

				shift
			done
		fi
	} | $cmd

}

