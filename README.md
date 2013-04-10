#virtual-server-control

A python command line tool for simplifying control and initiation of nginx virtual servers

#init

`vsc init <server_type>`

valid server types are html,rails,node,php

this command initializes the project with an nginx.conf file based on the server type provided

html template uses a simple doc root
php using fast cgi
rails using passenger
node using a proxy

#enable

`vsc enable`

enables the virtual server and reloads global nginx server configuration

#disable

`vsc disable`

disables the virtual server and reloads global nginx server configuration

#reload

`vsc reload`

reloads global nginx server configuration (use this if you manually alter the projects nginx.conf

#status

`vsc status`

show the status of the master nginx serve and list enabled servers

 

