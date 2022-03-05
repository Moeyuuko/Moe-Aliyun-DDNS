#-*- coding:utf-8 -*-

import requests
import key

class Moeip:
	def Requests_Url_Text(url):
		r = requests.get(url)
		return r.text

	def Get_Ip(Type = "ipv4"):
		if Type == "ipv6":
			return Moeip.Requests_Url_Text('http://ipv6-ip.moeyuuko.com/')
		elif Type == "ipv4":
			return Moeip.Requests_Url_Text('http://ipv4-ip.moeyuuko.com/')

if __name__ == '__main__':
	print (Moeip.Get_Ip("ipv4"))
	print (Moeip.Get_Ip("ipv6"))