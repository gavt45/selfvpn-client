#!/bin/bash


myinstaller(){
echo -n "Enter your username(/home/[username]/): "
read username

#wget -P /home/$username/selfvpn-client/ https://git.io/vpn -O openvpn-install.sh
#sed -i "s/read -N 999999 -t 0.001/#read -N 999999 -t 0.001/" openvpn-install.sh
#read -n1 -r -p "downloaded"

sudo chmod 0766 *.sh
sudo chmod 0766 *.py

sudo ./myopenvpn-install.sh


##############################################################

sed -i "s/10 120/5 10/" /etc/openvpn/server/server.conf

echo "[Unit]
Description=auto
After=network.target

[Service]
User=root
Type=simple
ExecStart=/home/$username/selfvpn-client/client.py
Restart=always

[Install]
WantedBy=multi-user.target" > selfvpn.service

sudo mv selfvpn.service /lib/systemd/system/
sudo chmod 644 /lib/systemd/system/selfvpn.service

sudo python3 client.py

k=$?

#if [ $k > 0 ]; then
#echo "Repair python then do these command:"
#echo "sudo python3 client.py"
#echo "sudo systemctl daemon-reload"
#echo "sudo systemctl start selfvpn.service"
#echo "sudo systemctl enable selfvpn.service"
#else
sudo systemctl daemon-reload
sudo systemctl start selfvpn.service
sudo systemctl enable selfvpn.service
#sudo systemctl status serlfvpn.service
#fi
}





myswitcher(){
#!/bin/bash
# This option could be documented a bit better and maybe even be simplified
# ...but what can I say, I want some sleep too

new_client () {
	# Generates the custom client.ovpn
	{
	cat /etc/openvpn/server/client-common.txt
	echo "<ca>"
	cat /etc/openvpn/server/easy-rsa/pki/ca.crt
	echo "</ca>"
	echo "<cert>"
	sed -ne '/BEGIN CERTIFICATE/,$ p' /etc/openvpn/server/easy-rsa/pki/issued/"$client".crt
	echo "</cert>"
	echo "<key>"
	cat /etc/openvpn/server/easy-rsa/pki/private/"$client".key
	echo "</key>"
	echo "<tls-crypt>"
	sed -ne '/BEGIN OpenVPN Static key/,$ p' /etc/openvpn/server/tc.key
	echo "</tls-crypt>"
	} > ~/"$client".ovpn
}


number_of_clients=$(tail -n +2 /etc/openvpn/server/easy-rsa/pki/index.txt | grep -c "^V")
if [[ "$number_of_clients" = 0 ]]; then
	echo
	echo "There are no existing clients!"
	exit
fi
echo
echo "Select the client to revoke:"
tail -n +2 /etc/openvpn/server/easy-rsa/pki/index.txt | grep "^V" | cut -d '=' -f 2 | nl -s ') '
#read -p "Client: " client_number
client_number=1
until [[ "$client_number" =~ ^[0-9]+$ && "$client_number" -le "$number_of_clients" ]]; do
	echo "$client_number: invalid selection."
	read -p "Client: " client_number
done
client=$(tail -n +2 /etc/openvpn/server/easy-rsa/pki/index.txt | grep "^V" | cut -d '=' -f 2 | sed -n "$client_number"p)
echo
#read -p "Confirm $client revocation? [y/N]: " revoke
revoke=y
until [[ "$revoke" =~ ^[yYnN]*$ ]]; do
	echo "$revoke: invalid selection."
	read -p "Confirm $client revocation? [y/N]: " revoke
done
if [[ "$revoke" =~ ^[yY]$ ]]; then
	cd /etc/openvpn/server/easy-rsa/
	./easyrsa --batch revoke "$client"
	EASYRSA_CRL_DAYS=3650 ./easyrsa gen-crl
	rm -f /etc/openvpn/server/crl.pem
	cp /etc/openvpn/server/easy-rsa/pki/crl.pem /etc/openvpn/server/crl.pem
	# CRL is read with each client connection, when OpenVPN is dropped to nobody
	chown nobody:"$group_name" /etc/openvpn/server/crl.pem
	echo
	echo "$client revoked!"
else
	echo
	echo "$client revocation aborted!"
fi

echo
echo "Provide a name for the client:"
#read -p "Name: " unsanitized_client
unsanitized_client=client
client=$(sed 's/[^0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-]/_/g' <<< "$unsanitized_client")
while [[ -z "$client" || -e /etc/openvpn/server/easy-rsa/pki/issued/"$client".crt ]]; do
	echo "$client: invalid name."
	read -p "Name: " unsanitized_client
	client=$(sed 's/[^0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-]/_/g' <<< "$unsanitized_client")
done
cd /etc/openvpn/server/easy-rsa/
EASYRSA_CERT_EXPIRE=3650 ./easyrsa build-client-full "$client" nopass
# Generates the custom client.ovpn
new_client
echo
echo "$client added. Configuration available in:" ~/"$client.ovpn"
}


key=$1
if [[ $key == "--switch" ]]; then
myswitcher
else
myinstaller
fi