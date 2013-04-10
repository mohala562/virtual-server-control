#!/usr/bin/python
import sys
import os
import subprocess
import json


def print_help():

	print """

vsrvctl <command> <subcommand>

		COMMAND		SUBCOMMAND		

		[status]

		init
						[html]
						rails
						php
						node

		enable
		disable
		reload

		help

"""

class VirtualServer:

	Templates = {

		'html' : """
			server {{
			    listen          80;
			    server_name     {name}.*;
			 
			    index           index.html;
			    root            {root_path}/public;
				}}
		""",

		'php': """
			server {{
			    listen          80;
			    server_name     {name}.*;
			 
			    index           index.php;
			    root            {root_path};
			 
			    location / {{
			        try_files   $uri $uri/ /index.php;
			    }}
			 
			    location ~* \.php$ {{
			        include fastcgi.conf; # I include this in http context, it's just here to show it's required for fastcgi!
			        try_files $uri =404;
			        fastcgi_pass 127.0.0.1:9000;
			    }}
			}}

		""",

		'rails': """
			server {{
				listen 80;
				server_name {name}.*;
				root {root_path}/public;
				rails_env development;
				passenger_enabled on;

			}}
		""",

		'node':"""

			server {{
				listen			80;
				server_name		{name}
				location / {{ 
					proxy_pass http://127.0.0.1 %(internal-port)
					expires 30d;
					access_log off; }}
				location ~* ^.+\.(jpg|jpeg|gif|png|ico|css|zip|tgz|gz|rar|bz2|pdf|txt|tar|wav|bmp|rtf|js|flv|swf|html|htm)$ {
			        root   {root_path}/public;
			    }}
		"""

	}

	vs_path_prefix='/var/www/'

	def __init__(self):

		self.gen_default_data()
		self.load_data()

	def _nginx_reload(self):

		
		ret=subprocess.call( [ "/opt/nginx/sbin/nginx" ,  "-s" , "reload" ] )
		if ret!=0:
			raise "error communicating with nginx, ensure that nginx is running"


	def gen_config(self,tp):
		
		F=open('./nginx.conf','w')

		nginx_conf=self.Templates[tp].format( **self.__dict__ )

		F.write( nginx_conf )

		F.close()

		print 'nginx.conf created: \n'

		print nginx_conf


	def gen_default_data(self):

		curdir=os.getcwd()
		self.name = os.path.basename(curdir)
		self.vs_path=os.path.join(self.vs_path_prefix,self.name)
		self.root_path=curdir

	def load_data(self):


		try:
			F=open('vs.json')
			data=json.load(F)
			F.close()
			for k in data:
				setattr(self,k,data[k])
		except:
			pass

	def control(self,com):

		if com=='enable' : self.enable()
		elif com=='disable' : self.disable()
		elif com=='reload': self._nginx_reload()
		elif com=='status': self.status()
		elif com=='help': print_help()


	def execute(self,command_list):

		try:
			command=command_list[0]
		except:
			command='status'


		if command=='init':
			
			try:
				server_type=command_list[1]
			except:
				server_type='html'

			if server_type in ('html','rails','node','php'):
				VS.gen_config(server_type)
			else:
				raise 'invalid server type'

		elif command=='control':

			try:
				subcommand=command_list[1]
			except:
				subcommand='status'

			if subcommand in ('enable','disable','reload','status'):
				VS.control(subcommand)
			else:
				raise 'invalid subcommand'

		elif command in ('enable','disable','reload','status'):
			VS.control(command)

		else:
			print_help()

			

	def enable(self):
		
		if os.path.islink(self.vs_path):
			print self.name + ' is already enabled'
			return True

		try:
			os.symlink( os.path.realpath("."), os.path.join( self.vs_path ) )

		except:
			raise
			return False

		self._nginx_reload()

		print self.name + ' enabled'
		return True

	def disable(self):

		if not os.path.exists(self.vs_path):
			print self.name + ' is already disabled'
			return True

		try:
			os.remove( self.vs_path )
		except:
			raise
			return False

		self._nginx_reload()

		print self.name + ' disabled'

	def reload(self):
		
		self._nginx_reload()

	def status(self):

		nginx_pid=self.check_nginx_proc()

		if nginx_pid >= 0:
			print "\nnginx server is running with pid " + str(nginx_pid)
		else:
			print "nginx server no running"
			return False

		self.list_virtual_servers()

		print

		return True


	def check_nginx_proc(self):

		F=open('/opt/nginx/logs/nginx.pid')
		pid=int(F.readline())
		F.close()

		for e in os.listdir('/proc'):
			if e.isdigit() and int(e)==pid:
				return pid

		return -1

	def list_virtual_servers(self):

		print '\nenabled virtual servers:'

		for e in os.listdir(self.vs_path_prefix):
			pth=os.path.join(self.vs_path_prefix,e)
			rpth=os.path.realpath(pth)
			if os.path.islink(pth) and os.path.isfile(os.path.join(rpth,'nginx.conf')):
				print '\t' + e


VS=VirtualServer()
VS.execute(sys.argv[1:])
