#-*- coding:utf-8 -*-

import requests

from typing import List
from Tea.core import TeaCore

from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_console.client import Client as ConsoleClient
from alibabacloud_tea_util.client import Client as UtilClient

import key

class Sample:
	def __init__(self):
		pass

	@staticmethod
	def create_client(
		access_key_id: str,
		access_key_secret: str,
	) -> Alidns20150109Client:
		"""
		使用AK&SK初始化账号Client
		@param access_key_id:
		@param access_key_secret:
		@return: Client
		@throws Exception
		"""
		config = open_api_models.Config(
			# 您的AccessKey ID,
			access_key_id=access_key_id,
			# 您的AccessKey Secret,
			access_key_secret=access_key_secret
		)
		# 访问的域名
		config.endpoint = f'alidns.cn-shenzhen.aliyuncs.com'
		return Alidns20150109Client(config)

class Moeip:
	@staticmethod
	def Requests_Url_Text(url):
		r = requests.get(url)
		return r.text

	@staticmethod
	def Get_Ip(Type = "ipv4"):
		if Type == "ipv6":
			return Moeip.Requests_Url_Text('http://ipv6-ip.moeyuuko.com/')
		elif Type == "ipv4":
			return Moeip.Requests_Url_Text('http://ipv4-ip.moeyuuko.com/')
	
	@staticmethod
	def push_ip(record_id,rr,type,value,ttl=600) -> None:
		client = Sample.create_client(key.access_key_id, key.access_key_secret)
		update_domain_record_request = alidns_20150109_models.UpdateDomainRecordRequest(
			record_id=record_id,
			rr=rr,
			type=type,
			value=value,
			ttl=ttl
		)
		resp = client.update_domain_record(update_domain_record_request)
		#print (resp)
		ConsoleClient.log(UtilClient.to_jsonstring(TeaCore.to_map(resp)))

	@staticmethod
	def Get_RecordId(sub_domain) -> None:
		client = Sample.create_client(key.access_key_id, key.access_key_secret)
		describe_sub_domain_records_request = alidns_20150109_models.DescribeSubDomainRecordsRequest(
			sub_domain=sub_domain
		)
		resp = client.describe_sub_domain_records(describe_sub_domain_records_request)
		#ConsoleClient.log(UtilClient.to_jsonstring(TeaCore.to_map(resp)))
		return TeaCore.to_map(resp)["body"]["DomainRecords"]["Record"][0]["RecordId"]
	



if __name__ == '__main__':
	#print (Moeip.Get_Ip("ipv4"))
	#print (Moeip.Get_Ip("ipv6"))
	Moeip.push_ip(Moeip.Get_RecordId('test.moe123.top'),'test','AAAA',Moeip.Get_Ip("ipv6"),600)