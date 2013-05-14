#!/bin/sh

log_error() {
	echo "$*" >&2
}

err_exit() {
	err_code=$1
	shift
	log_error "$*" 
	exit $err_code
}	

help_exit() {
	help_syntax_msg
	exit 1
}

help_syntax_msg() {
	log_error $( echo "[${CONTEXT}]"  | sed -e 's|_|/|g' )
	log_error $( echo $( eval "echo \$${CONTEXT}cmds" ) | sed -e 's|_|/|g' )
}


parse_CMD() {
	arg=$1;	shift
	echo $arg;

	for branch in $( eval "echo \$${CONTEXT}cmds" )
	do
		if [ "${arg}_" = "${branch}" ]; then
			CONTEXT=${CONTEXT}${branch}
			parse_CMD "$@"

		else
			if [ "$arg" = "${branch}" ]; then
				CMD=${CONTEXT}${branch} "$@"
			else
				CMD=''
			fi
		fi
	done
}

