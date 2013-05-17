#!/usr/bin/python

import os
import sys
import string
import uuid
import vmx_op


def log_error(msg):
	sys.stderr.write(msg+'\n')

def is_valid_db_q(db):
	return os.path.isdir(db)

def is_valid_record_q(db):
	return os.path.isfile(db)

def path_of_record(db,i):
	return os.path.join(db,i)

def id_exists_q(db,i):
	return os.path.exists( path_of_record(db,i) )

def create(db,i,data):

	if not i:
		i=str(uuid.uuid1())

	if id_exists_q(db,i):
		raise Exception("db_id_not_unique")

	data['.id']=i

	vmx_op.dump_path( path_of_record(db,i) , data)

	return data



def read(db,i):
 
	log_error(path_of_record(db,i))

	if not id_exists_q(db,i):
		raise Exception("db_no_id")
	
	data=vmx_op.load_path( path_of_record(db,i) ) 

	return data

def update(db,i,delta):

	if not id_exists_q(db,i):
		raise Exception("db_no_id")

	data=read(db,i)

	data.update(delta)

	print data

	vmx_op.dump_path( path_of_record(db,i) , data)

	return data

def delete(db,i):

	if not id_exists_q(db,i):
		raise Exception("db_no_id")

	os.remove( path_of_record(db,i) )

	return { '.id' : i }

def ids(db):

	if not is_valid_db_q(db):
		raise Exception("invalid_db")

	ids=os.listdir(db)

	return { '.ids' : string.join(ids,' ') }




def db_task(data):

	try:
		op = data.pop('.op')
	except:
		raise Exception("no_db_op_given")

	try:
		db = data.pop('.db')
	except:
		raise Exception("no_db_given")

	op=op[0].lower()

	if op == 'c':
		i = data.pop('.id','')
		return create(db,i,data)

	if op == 'i':
		return ids(db)


	try:
		i = data.pop('.id')
	except:
		raise Exception("no_id_given")

	if op == 'u':
		return update(db,i,data)

	if op == 'd':
		return delete(db,i)

	return read(db,i)



if __name__=='__main__':

	input_mode , output_mode = vmx_op.cmdline_parse_stream_mode()	

	in_data = vmx_op.load( sys.stdin , input_mode=input_mode )
	out_data = db_task( in_data )

	vmx_op.dump( out_data, sys.stdout , output_mode=output_mode ) 


	








