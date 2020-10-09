import requests
import socket
import base64
import ast
import datetime
import json
import os
import sys
import http.client

#Interaction with server#

def register(url):
	#data = {'port':port}
	url = url + "/register"
	res = requests.post(url)
	selfvpn_conf = open('selfvpn.conf','w')

	if res.json()['code'] == 0:
		print("You autorized",file=sys.stdout)
		selfvpn_conf.write(json.dumps({"uid":res.json()["uid"],"token":res.json()["token"]}))
	else:
		print(res.json()['msg']['name']+': ' + res.json()['msg']['description'],file=sys.stderr)
	selfvpn_conf.close()


def push(url,port):
	selfvpn_conf = open('selfvpn.conf')
	dictt = json.loads(g.read())
	data = {
		"uid":dictt["uid"],
		"token":dictt["token"],
		"port":port
	}
	url = url + "/push"
	res = requests.post(url,data=data)
	selfvpn_conf.close()


def update(url,client):
	client_ovpn = open("/root/"+client+".ovpn")
	selfvpn_conf = open("~/selfvpn.conf")
	dictt = json.loads(selfvpn_conf.read())
	data = {
		"uid":dictt["uid"],
		"token":dictt["token"],
		"config":encode(client_ovpn.read())
	}
	url = url + "/update"
	res = requests.post(url,data=data)
	client_ovpn.close()
	selfvpn_conf.close()

#Changing config files#

def addconf(client):
	client += ".ovpn"
	client_ovpn = open("/root/"+client)
	selfvpn_conf = open("~/selfvpn.conf")

	s = client_ovpn.read()
	port = s.split()[8]
	ip_in_config = s.split()[6]
	dictt = json.loads(selfvpn_conf.read())
	dictt.update({"ip":ip_in_config,"port":port})
	selfvpn_conf.close()

	selfvpn_conf = open("selfvpn.conf","w")
	selfvpn_conf.write(json.dumps(dictt))

	client_ovpn.close()
	selfvpn_conf.close()


def change_ip(client,ip):
	f = open("/root/"+client+".ovpn")
	s = f.read().split()
	f.close()
	s[6] = ip
	f = open("/root/"+client,"w")
	f.write(" ".join(s))
	f.close()


def chahge_port(client,port):
	f = open("/root/"+client+".ovpn")
	s = f.read().split()
	f.close()
	s[8] = port
	f = open("/root/"+client,"w")
	f.write(" ".join(s))
	f.close()

#Secondary functions#

def encode(s):
	s_bytes = s.encode('ascii')
	base64_bytes = base64.b64encode(s_bytes)
	base64_msg = base64_bytes.decode('ascii')
	return base64_msg


def get_ip():
	conn = http.client.HTTPConnection("ifconfig.me")
	conn.request("GET", "/ip")
	ip = str(conn.getresponse().read())[2:-1]
	return ip

url = "http://127.0.0.1:5000"
client = "client"

if not os.path.exists("~/selfvpn.conf"):
	ip = get_ip()
	port = input("input your forwarding port\n")
	register(url)
	change_ip(client,ip)
	change_port(client,port)
	addconf(client)
	print("regiter ok")

while(True):

	client_ovpn = open("/root/"+client+".ovpn")
	selfvpn_conf = open("selfvpn.conf")

	s_cli = client_ovpn.read()
	s_self = json.loads(selfvpn_conf.read())

	client_ovpn.close()
	selfvpn_conf.close()

	ip = get_ip()
	ip_in_my_config = s_self["ip"]
	ip_in_config = s_cli.split()[6]
	port_in_my_config = s_self["port"]
	port_in_config = s_cli.split()[8]

	if ip != ip_in_config:
		change_ip(client,ip)

	if ip_in_config != ip_in_my_config or port_in_config != port_in_my_config:
		addconf(client)
		push(url,port_in_my_config)
		update(url,client)

		
#что за конфиг берет гет
#насколько тяжелые функции open and read

#каждые н минут 
