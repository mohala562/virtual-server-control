#MAC ADDR functions

mac_to_int = lambda s: s.strip.split(':')
int_to_mac = lambda n: [ hex(n)[2:][i:i+1] for i in range() ]

def validate_mac_addr(mac_addr_s):

	build_err_msg = lambda err: 'invalid macaddr' + ': ' + err
	
	MAX_MAC_INT=281474976710655

	if mac_addr_s not in string.hexdigits + ':' :
		return {'type':'error',
				'msg': build_err_msg('invalid symbols in mac address'),
			   }


	n=mac_to_int(mac_addr_s)


	if 0 > n and MAX_MAC_INT < n:
		return {'type':'error',
		        'msg' : build_err_msg('mac address out of range'),
		        }

	return True


def gen_mac_addr(mac_addr_seed):
#this generator iterates a mac string
#super basic just iterates the last octet
#takes a ':'' mac address string
#returns an iterator whick yields the next mac address in the sequence

	n=mac_to_int(mac_addr_seed)
	n=n+1
	yield int_to_mac(n)



num_name_split = lambda s:  apply( lambda X,i: ( X[:i+1], X[i+1:] ) , ( s, s.strip.rfind('_') ) ) 

def validate_num_name(name_s):

	build_err_msg = lambda err: 'invalid numeric name' + ': ' + err

	if not has_valid_chars(string.printable) :
		return {'type':'error',
				'msg': build_err_msg('invalid symbols in numeric name'),
			   }

	s, n = num_name_split(name_s)

	if s=='':
		return {'type':'error',
				'msg': build_err_msg('no numeric postfix'),
				}
	if s=='_':
		return {'type':'error',
				'msg': build_err_msg('no base name prefix'),
				}

	return True


def gen_num_name(name_seed):
#this generator iterates a name with a '_%i' postfix
#takes a name string
#returns an iterator whick yields the name in the sequence

	

	r=validate_num_name(name_seed)
	if not r:
		sys.stderr.write(r['msg'])




	s, n = num_name_split(name_seed)
	n=n+1
	yield string.join(s,n)


Generators = {
	'num_name' : gen_num_name,
	'mac_addr' : gen_mac_addr,
}
