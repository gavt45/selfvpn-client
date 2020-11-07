import requests
import json
import base64
import os
import subprocess

def get(url):
	f = open("/root/selfvpn.conf")
	a = json.loads(f.read())
	data = {
		"uid":a["uid"],
		"token":a["token"]
	}
	url = f"{url}/get"
	res = requests.post(url,data=data)
	f.close()
	return res

#None##################

def encode(s):
	s_bytes = s.encode("ascii")
	base64_bytes = base64.b64encode(s_bytes)
	base64_msg = base64_bytes.decode("ascii")
	return base64_msg
	
#######################

url = "http://10.0.2.4:5000"

#start
if not os.path.exists("/root/client.conf"):
	#f = open("/root/client.ovpn")#None
	res = get(url)
	base64_msg = res.json()
	'''
	base64_bytes = base64_msg.encode("ascii")
	config_bytes = base64.b64decode(base64_bytes)
	config = config_bytes.decode("ascii")'''
	#f.close()#None
	print(base64_msg)
	f = open("/root/client.conf","w")
	f.write(config)
	f.close()
	subprocess.run(["sudo", "openvpn", "--client", "--config", "/root/client.conf"])
#stop
else:
	path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "/root/client.conf")
	os.remove(path)	
	print("removed")