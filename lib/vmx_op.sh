#!/bin/sh
# wrappers for vmx_op.py

vmx_op_cmd="./lib/vmx_op.py"

#help_msg="vmx_op [ -i <vmx_file_0> -i <vmx_file_1> ] [ -e 'vmx_op_expr' -e ... ] > output_file"

vmx_op () {

	cmd=$vmx_op_cmd

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



#the current vmx file
touch '_'
cvmx='_'

vmx_set_current_file() {

	cvmx="$*"

}

vmx_get() {

	vmx_op -i "$cvmx" "$@" 
}

vmx_change() {

	vmx_op -i "$cvmx" "$@" > "$cvmx"
}

alias v=vmx_op
alias c=vmx_set_current_file
alias g=vmx_get
alias s=vmx_change