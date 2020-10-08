import requests
import socket
import base64
import ast
import datetime
import json
import os
import sys

def register(url):
	#data = {'port':port}
	url = url + "/register"
	res = requests.post(url)
	g = open('selfvpn.conf','w')

	if res.json()['code'] == 0:
		print("You autorized",file=sys.stdout)
		g.write(json.dumps(res.json()))
		#print(res.json())
	else:
		print(res.json()['msg']['name']+': ' + res.json()['msg']['description'],file=sys.stderr)
	g.close()


def push(url,port):
	g = open('selfvpn.conf')
	a = json.loads(g.read())
	data = {
		'uid':a['uid'],
		'token':a['token'],
		'port':port
	}
	url = url + "/push"
	res = requests.post(url,data=data)
	g.close()


def encode(s):
	s_bytes = s.encode('ascii')
	base64_bytes = base64.b64encode(s_bytes)
	base64_msg = base64_bytes.decode('ascii')
	return base64_msg


def addconf(client):
	client += ".ovpn"
	f = open("/root/"+client)
	s = f.read()
	base64_msg = encode(s)
	g = open('selfvpn.conf')
	a = json.loads(g.read())
	a.update({'config':base64_msg})
	g.close()
	g = open('selfvpn.conf','w')
	g.write(json.dumps(a))
	f.close()
	g.close()


def change_conf(client,ip,port):
	client += ".ovpn"
	f = open("/root/"+client)
	#print(f.read()[25:50])
	s = f.read().split('\n')
	s[3] = "remote " + ip+ " " + port
	f = open("/root/"+client,'w')
	f.write('\n'.join(s))
	f.close()


def update(url):
	g = open('selfvpn.conf')
	a = json.loads(g.read())
	data = {
		'uid':a['uid'],
		'token':a['token'],
		'config':a['config']
	}
	url = url + "/update"
	res = requests.post(url,data=data)
	g.close()


url = "http://127.0.0.1:5000"
client = "client"
#ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
#port = input('input your forwarding port\n')

if not os.path.exists("selfvpn.conf"):
	ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
	port = input('input your forwarding port\n')
	register(url)
	change_conf(client,ip,port)
	addconf(client)
	print("regiter ok")

while(True):

	f = open("/root/"+client+".ovpn")
	g = open("selfvpn.conf")

	sf = f.read()
	base64_msg = encode(sf)
	sg =  json.loads(g.read())

	f.close()
	g.close()

	ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0]
	port = sf.split()[8]
	ip_in_config = sf.split()[6]

	if ip != ip_in_config:
		change_conf(client,ip,port)

	if base64_msg != sg['config']:
		addconf(client)
		push(url,port)
		update(url)

		
#что за конфиг берет гет
#насколько тяжелые функции open and read

#каждые н минут 
