import requests
import socket
import base64
import datetime
import json
import os
import sys
import http.client

#Interaction with server

def register(url):
	url = url + "/register"
	res = requests.post(url)
	selfvpn_conf = open("../selfvpn.conf","w")

	if res.json()['code'] == 0:
		print("You autorized",file=sys.stdout)
		selfvpn_conf.write(json.dumps({"uid":res.json()["uid"],"token":res.json()["token"],"ip":"","port":""}))
	else:
		print(res.json()['msg']['name']+': ' + res.json()['msg']['description'],file=sys.stderr)
	selfvpn_conf.close()


def push(url,s_self):
	dictt = s_self
	data = {
		"uid":dictt["uid"],
		"token":dictt["token"],
		"port":dictt["port"]
	}
	url = url + "/push"
	res = requests.post(url,data=data)


def update(url,client,s_cli,s_self):
	dictt = s_self
	data = {
		"uid":dictt["uid"],
		"token":dictt["token"],
		"config":encode(s_cli)
	}
	url = url + "/update"
	res = requests.post(url,data=data)

#Changing config files

def addconf(client,s_cli,s_self):
	s = s_cli
	port_in_config = s.split()[7]
	ip_in_config = s.split()[6]
	dictt = s_self
	dictt["ip"] = ip_in_config
	dictt["port"] = port_in_config

	selfvpn_conf = open("../selfvpn.conf","w")
	selfvpn_conf.write(json.dumps(dictt))
	selfvpn_conf.close()


def changeconf(client,ip,port,s_cli):
	s = s_cli.split("\n")
	s[3] = "remote " + ip + " " + port
	f = open("/root/"+client+".ovpn","w")
	s  = "\n".join(s)
	f.write(s)
	f.close()
	return s

'''
def change_ip(client,ip,s_cli):
	s = s_cli.split(" ")
	s[6] = ip
	f = open("/root/"+client+".ovpn","w")

	f.write(" ".join(s))
	f.close()


def change_port(client,port,s_cli):
	s = s_cli.split(" ")
	s[7] = ""
	s[8] = port
	f = open("/root/"+client+".ovpn","w")
	f.write(" ".join(s))
	f.close()
'''
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

url = "http://127.0.0.1:5000"
client = "client"

if not os.path.exists("../selfvpn.conf"):
	ip = get_ip()
	port = input("input your forwarding port\n")
	register(url)

	client_ovpn = open("/root/"+client+".ovpn")
	selfvpn_conf = open("../selfvpn.conf")

	s_cli = client_ovpn.read()
	s_self = selfvpn_conf.read()

	client_ovpn.close()
	selfvpn_conf.close()

	s_cli = changeconf(client,ip,port,s_cli)
	addconf(client,s_cli,s_self)

	print("regiter ok")

while(True):

	client_ovpn = open("/root/"+client+".ovpn")
	selfvpn_conf = open("../selfvpn.conf")

	s_cli = client_ovpn.read()
	s_self = json.loads(selfvpn_conf.read())

	client_ovpn.close()
	selfvpn_conf.close()

	ip = get_ip()
	ip_in_my_config = s_self["ip"]
	ip_in_config = s_cli.split()[6]

	port_in_my_config = s_self["port"]
	port_in_config = s_cli.split()[7]

	if ip != ip_in_config:
		changeconf(client,ip,port_in_config,s_cli)

	if ip_in_config != ip_in_my_config or port_in_config != port_in_my_config:
		addconf(client,s_cli,s_self)
		push(url,s_self)
		update(url,client,s_cli,s_self)

