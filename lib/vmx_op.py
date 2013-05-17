#!/usr/bin/python
####################################################
# op
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

sh_to_key = lambda k: k.replace('__',':').replace('_','.')
to_sh_key = lambda k: k.replace(':','__').replace('.','_').replace(' ','')


def open_read(fpth):

	try:
		f=open(fpth,'r')
	except:
		sys.stderr.write(\
			'> could not open vmx for reading\n'\
			+ sys.exc_info()[0]\
		)
		raise

	return f

def open_write(fpth):

	try:
		f=open(fpth,'w')
	except:
		sys.stderr.write('> could not open vmx for writing\n')
		raise

	return f

def parse_line(s,input_mode='vmx'):
	#takes a string representing the line
	#returns a dict representing the parsed line's content
	
	build_err_msg = lambda err: 'error parsing string' + ': ' + err

		#handle empty line

	s=s.strip().strip(',').strip() #strippin'
	if not s: 
		return { 'type' : None }

	#handle line sep
	X=[ t.strip().strip('"') for t in s.split('=') ]
	
	#translate based on input mode
	if input_mode=='sh':

		X[0] = sh_to_key(X[0])

	#detect filter stmt
	if X[0]=='!':
		if len(X) <= 1:
			return { 'type' : 'error' ,
				 	 'action' : 'skip',
				 	 'msg' : build_err_msg('filter key is empty!'),
			  		 }
		key=X[1:].split()[0]
		return { 'type' : 'filter',
				 'action' : 'remove',
				 'key' : key }

	#validate key
	valid_chars = string.letters + string.digits + '.:'
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
	valid_chars = string.printable + ' '
	if not has_valid_chars(X[1],valid_chars):
		return { 'type' : 'error' ,
				 'action' : 'skip',
				 'msg' : build_err_msg('value contains invalid characters\nvalid key chars: ' + valid_chars),
			   }


	#filtered down to regular data pair
	return { 'type' : 'data',
	         'key' : X[0] ,
	         'val' : X[1] }


def load(f,input_mode='vmx'):
#takes open file object representing the vmx file
#returns parsed dict represent the vmx file

	build_err_msg = lambda err, line_num: '> vmx(' + str(line_num) + ') ' + d['msg']

	VMX_Data={}
	order=[]
	filter_mode=None
	filter_keys=[]


	L=[]
	
	while True:
		
		l=f.readline()
		if not l: break
		
		for stmt in l.split(';'):
			L.append(stmt)

	c=0
	for l in L:

		c=c+1

		d=parse_line(l,input_mode=input_mode)

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
		VMX_Data=filter_data(VMX_Data,filter_keys,filter_mode)
		


	return VMX_Data

def dump(D,f,output_mode='vmx'):

	if D.has_key('_order'):
		unordered_keys = [ k for k in D if k not in D['_order'] ]
		orderered_keys = [ k for k in D if k in D['_order'] and D.has_key(k) ]
		keys = sorted( unordered_keys , key=lambda x: x[0] ) + orderered_keys 
	else:
		keys = D.keys()

	keys=[ k for k in keys if k[0]!='_' ]
	
	if output_mode == 'sh':
		D = dict( [ ( to_sh_key(k) , D[k] ) for k in keys ] )
		keys = [ to_sh_key(k) for k in keys ]

	for k in keys:
		
		if output_mode == 'sh':
			f.write( to_sh_key(k) + "='" + D[k] + "'\n")

		else:
			f.write( k + ' = "' + D[k] + '"\n')

	if output_mode == 'sh':
		f.write( "_keys=" + string.join(keys,"' '") + "\n")


def load_path(fpth):
	F=open_read(fpth)
	data=load(F)
	F.close()
	return data

def dump_path(fpth,D):
	F=open_write(fpth)
	dump(D,F)
	F.close()

def filter_data(D,keys,mode):

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

##cmdline interface

def cmdline_parse_stream_mode():

	output_mode = 'vmx'
	input_mode  = 'vmx'

	if len(sys.argv) > 3:
		log_error( usage_msg() )
		return

	if len(sys.argv) == 3:
		if sys.argv[1] == '--input-mode':
			input_mode=sys.argv[2]
			if input_mode not in ['sh','vmx']:
				return
		elif sys.argv[1] == '--output-mode':
			output_mode=sys.argv[2]
			if output_mode not in ['sh','vmx']:
				return
		else:
			return

	return ( input_mode , output_mode )

if __name__=="__main__":


	input_mode , output_mode = cmdline_parse_stream_mode()

	VMX = load( sys.stdin, input_mode=input_mode )
	dump( VMX, sys.stdout, output_mode=output_mode )

