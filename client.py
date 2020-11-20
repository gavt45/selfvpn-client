#!/usr/bin/python3

import requests
import socket
import base64
import datetime
import json
import os
import subprocess
import sys
import http.client
import portforwardlib

#Interaction with server

def register(url):
	url = "{}/register".format(url)
	res = requests.post(url)
	dictt = res.json()
	selfvpn_conf = open("/root/selfvpn.conf","w")

	if dictt["code"] == 0:
		print("You autorized",file=sys.stdout)
		selfvpn_conf.write(json.dumps({"uid":dictt["uid"],"token":dictt["token"],"ip":"","port":""}))
	else:
		print(f"{dictt['msg']['name']}: {dictt['msg']['description']}",file=sys.stderr)
		#print(res.json()["msg"]["name"]+": " + res.json()["msg"]["description"],file=sys.stderr)
	
	selfvpn_conf.close()


def push(url,s_self):
	dictt = json.loads(s_self)
	data = {
		"uid":dictt["uid"],
		"token":dictt["token"],
		"port":dictt["port"]
	}
	url = "{}/push".format(url)
	res = requests.post(url,data=data)
	#if res.json()["code"] != 0:
		#print(res.json())
		#print(f"{res.json()['msg']['name']}: {res.json()['msg']['description']}",file=sys.stderr)
	

def update(url,client,s_cli,s_self):
	dictt = json.loads(s_self)
	data = {
		"uid":dictt["uid"],
		"token":dictt["token"],
		"config":encode(s_cli)
	}
	url = "{}/update".format(url)
	res = requests.post(url,data=data)
	#if res.json()["code"] != 0:
		#print(res.json())
		#print(f"{res.json()['msg']['name']}: {res.json()['msg']['description']}",file=sys.stderr)


#Changing config files

def login():
	global last
	f_read = open("/var/log/syslog")
	last_line = f_read.readlines()[-1]
	if last_line != last:
		if "client-instance restarting" in last_line:
			return False
		elif "initialized with 256 bit key" in last_line:
			return True
		last = last_line
	f_read.close()


def addconf(client,s_cli,s_self):
	s = s_cli
	port_in_config = s.split()[7]
	ip_in_config = s.split()[6]
	dictt = json.loads(s_self)
	dictt["ip"] = ip_in_config
	dictt["port"] = port_in_config

	selfvpn_conf = open("/root/selfvpn.conf","w")
	selfvpn_conf.write(json.dumps(dictt))
	selfvpn_conf.close()


def changeconf(client,ip,port,s_cli):
	s = s_cli.split("\n")
	s[3] = "remote {} {}".format(ip,port)
	f = open("/root/{}.ovpn".format(client),"w")
	s  = "\n".join(s)
	f.write(s)
	f.close()
	return s


#Secondary functions

def encode(s):
	s_bytes = s.encode("ascii")
	base64_bytes = base64.b64encode(s_bytes)
	base64_msg = base64_bytes.decode("ascii")
	return base64_msg


def get_ip():
	conn = http.client.HTTPConnection("ifconfig.me")
	conn.request("GET", "/ip")
	ip = str(conn.getresponse().read())[2:-1]
	return ip

url = "http://10.0.2.7:5000"
client = "client"
log_status = "logout" #False - pass, True - switch status
last = ""

#First start
if not os.path.exists("/root/selfvpn.conf"):

	client_ovpn = open(f"/root/{client}.ovpn")
	#selfvpn_conf = open("/root/selfvpn.conf")

	s_cli = client_ovpn.read()
	#s_self = selfvpn_conf.read()

	client_ovpn.close()
	#selfvpn_conf.close()

	ip = get_ip()
	while True:
		port = input("input your forwarding port(if you aren't behind the NAT print n): ")
		if(port == "n" or port >= "0" and port < "65536" ):
			if port == "n":
				port = 1194
			else:
				port = int(port)
				proto = s_cli.split()[4]
				res = portforwardlib.forwardPort(port,1194,None,None,True,proto,0,"selfvpn service",True)
		break

	register(url)

	selfvpn_conf = open("/root/selfvpn.conf")
	s_self = selfvpn_conf.read()
	selfvpn_conf.close()

	s_cli = changeconf(client,ip,port,s_cli)
	addconf(client,s_cli,s_self)
	push(url,s_self)
	update(url,client,s_cli,s_self)
	print("regiter ok")
	
#Daemon
else:
	while(True):

		client_ovpn = open("/root/{}.ovpn".format(client))
		selfvpn_conf = open("/root/selfvpn.conf")

		s_cli = client_ovpn.read()
		s_self = selfvpn_conf.read()

		client_ovpn.close()
		selfvpn_conf.close()

		ip = get_ip()
		ip_in_my_config = json.loads(s_self)["ip"]
		ip_in_config = s_cli.split()[6]

		port_in_my_config = json.loads(s_self)["port"]
		port_in_config = s_cli.split()[7]

		if ip != ip_in_config:
			changeconf(client,ip,port_in_config,s_cli)

		if ip_in_config != ip_in_my_config or port_in_config != port_in_my_config:
			addconf(client,s_cli,s_self)
			proto = s_cli.split()[4]
			res = portforwardlib.forwardPort(port_in_config,1194,None,None,True,proto,0,"selfvpn service",True)
			push(url,s_self)
			update(url,client,s_cli,s_self)

		if login() and log_status == "logout":
			log_status = "login"
		elif not login() and log_status == "login":
			log_status = "logout"
			subprocess.run(["sudo", "./starter.sh", "--switch"], stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
			update(url,client,s_cli,s_self)

