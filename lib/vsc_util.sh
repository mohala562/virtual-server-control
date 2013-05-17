#!/bin/sh

vsc_root='.'
db_root='./db'

_vmx_op="${vsc_root}/lib/vmx_op.py"
_vmx_db="${vsc_root}/lib/vmx_db.py"

vmx_input () {

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
		echo
	}
}

vmx_db() {
	vmx_input "$@" | $_vmx_db
}

vmx_op_() {
	vmx_input "$@" | $_vmx_op
}

vmx_receive() {
	__data_prefix=$1
	shift
	for stmt in $( $_vmx_op --output-mode sh )
	do
		eval "${__data_prefix}_${stmt}"
	done
}

vmx_send() {

	__data_prefix=$1
	shift
	for var in "$@"
	do
		eval "echo ${var#${__data_prefix}_}=\$${var}" 
	done | $_vmx_op --input-mode sh

}

vmx_load_record() {

	db="$1"
	db_path="${db_root}/$1"
	id="$2"

	for stmt in $(	{ echo .op = "read" ; echo .db = "$db_path" ; echo .id = "$id" ; echo ;} | $_vmx_db --output-mode sh )
	do
		echo "${db}_${stmt}"
	done	

}

vmx_save_record() {	

	db="$1"
	db_path="${db_root}/$1"
	id="$2"
	[ -z "$2" ] && id=$( eval "echo \$${db}__id" )

	{
		echo .op = update
		echo .db = "$db_path"
		echo .id = "$id" 

		for var in $( eval "echo \$${db}__keys" )
		do
			eval "echo ${var#${db}_}=\$${var}" 
		done

	}

}


vmx_db_list() {
	ls $1
}

load_entry() { eval "${1}_${2}"; }
append_key() { eval "${1}_"; }


load() {

	__data_prefix=$1
	for stmt in $( $_vmx_op --output-mode sh )
	do
		load_entry
	done
}

dump() {
	
	for var in "$@"
	do
		eval "echo ${var#${__data_prefix}_}=\$${var}" 
	done | $_vmx_op --input-mode sh

}

receive() {

	for stmt in $( $_vmx_op --output-mode sh "$@" )
	do
		eval "$stmt"
	done

}

send() {

	for var in "$@"
	do
		eval "echo ${var#}=\$${var}" 
	done | $_vmx_op --input-mode sh
}

sendf() {

	for f in "$@"
	do
		cat ${f}
	done | $_vmx_op

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

