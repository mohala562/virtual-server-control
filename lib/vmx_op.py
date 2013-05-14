#!/usr/bin/python
####################################################
# vmx_op
###################################################
# Nick Jordan
###################################################
# Query and manipulate vmx files from the command line
# great for batch processing
##################################################

import sys
import os
import re
import string
import types

def log_error(msg):
	sys.stderr.write(msg+'\n')
has_valid_chars = lambda s,chars: s.translate(None, chars) == '' 

def vmx_filter_data(D,keys,mode):

	order=D['_order']
	keys=set(keys.remove('_order'))

	if mode=='-':
		keys=[ k for k in D.keys() if k not in keys ]
	if mode=='+':
		keys=[ k for k in keys if k in D.keys() ]
	
	D = dict( [ (k,D[k]) for k in keys if k in D.keys()] )

	for k in D:
		D['_order'].remove(k)

	return D


def vmx_parse_line(s):
	#takes a string representing the line
	#returns a dict representing the parsed line's content
	
	build_err_msg = lambda err: 'error parsing string' + ': ' + err

		#handle empty line

	s=s.strip(',').strip()
	if not s: 
		return { 'type' : None }

	if s[0]=='!':
		key=s[1:].split()[0]
		return { 'type' : 'filter',
				 'action' : 'remove',
				 'key' : key }

	#handle line sep
	X=[ t.strip().strip('"') for t in s.split('=') ]
	
	#validate key
	valid_chars = string.letters + string.digits + '.:_'
	if not has_valid_chars(X[0],valid_chars):
		return { 'type' : 'error' ,
				 'action' : 'skip',
				 'msg' : build_err_msg('key contains invalid characters\nvalid key chars: ' + valid_chars),
			   }

	if len(X)==1:
		key=X[0]
		return { 'type' : 'filter',
				 'action' : 'add',
				 'key' : key }

	if len(X)!=2:
		return { 'type' : 'error' ,
				 'action' : 'skip',
				 'msg' : build_err_msg('line must zero or one "="'),
			   }

	if '{' in X[1] and '}' in X[1]:
		return { 'type' : 'substitution',
				 'key' : X[0],
				 'fmt_str' : X[1],
				}


	#validate value
	valid_chars = string.printable
	if not has_valid_chars(X[1],valid_chars):
		return { 'type' : 'error' ,
				 'action' : 'skip',
				 'msg' : build_err_msg('value contains invalid characters\nvalid key chars: ' + valid_chars),
			   }


	#filtered down to regular data pair
	return { 'type' : 'data',
	         'key' : X[0] ,
	         'val' : X[1] }


def vmx_load(f):
#takes open file object representing the vmx file
#returns parsed dict represent the vmx file

	build_err_msg = lambda err, line_num: '> vmx(' + str(line_num) + ') ' + d['msg']

	VMX_Data={}
	order=[]
	filter_mode=None
	filter_keys=[]


	c=0
	while True:

		c=c+1

		l=f.readline()
		if not l: break

		d=vmx_parse_line(l)

	# handle parse line errors
		if d['type']=='error':
			if d['action']=='skip':
				log_error( build_err_msg( d['msg'],c ) )
				log_error( '> skipping line')
				continue
			else:
				break

		if d['type']=='data':
			if d['key'] not in order:
				order.append(d['key'])
			VMX_Data.update( { d['key'] : d['val'] } )

		if d['type']=='filter':
			
			if d['action']=='remove':
			
				if not filter_mode:
					filter_mode='-'
				if filter_mode=='-':
					filter_keys.append(d['key'])

			if d['action']=='add':
			
				if filter_mode!='+':
					filter_mode='+'
					filter_keys=[]
				filter_keys.append(d['key'])

		if d['type']=='substitution':
			if d['key'] not in order:
				order.append(d['key'])
			VMX_Data[ d['key'] ] = d['fmt_str'].format(**VMX_Data)


 	VMX_Data['_order']=order

	if filter_mode:
		VMX_Data=vmx_filter_data(VMX_Data,filter_keys,filter_mode)
		


	return VMX_Data


def vmx_open_read(fpth):

	try:
		f=open(fpth,'r')
	except:
		sys.stderr.write(\
			'> could not open vmx for reading\n'\
			+ sys.exc_info()[0]\
		)
		raise

	return f

def vmx_open_write(fpth):

	try:
		f=open(fpth,'w')
	except:
		sys.stderr.write(\
			'> could not open vmx for writing\n'\
			+ sys.exc_info()[0]\
		)
		raise

	return f

def vmx_dump(D,f):
	for k in D['_order']:
		if k[0]!='_':
			f.write( k + ' = "' + D[k] + '"\n')

##cmdline interface

if __name__=="__main__":

	if len(sys.argv) > 1:
		print 'usage'
		sys.exit(1)


	VMX = vmx_load( sys.stdin )
	vmx_dump( VMX, sys.stdout )

