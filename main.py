#-*- coding:utf-8 -*-

import requests

from typing import List
from Tea.core import TeaCore

from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_console.client import Client as ConsoleClient
from alibabacloud_tea_util.client import Client as UtilClient

import Config

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
	
	def __init__ (self, access_key_id: str,access_key_secret: str):
		self.client = Sample.create_client(access_key_id, access_key_secret)
	
	@staticmethod
	def push_ip(self,RecordId,rr,type,value,ttl=600) -> None:
		update_domain_record_request = alidns_20150109_models.UpdateDomainRecordRequest(
			record_id=RecordId,
			rr=rr,
			type=type,
			value=value,
			ttl=ttl
		)
		resp = self.client.update_domain_record(update_domain_record_request)
		ConsoleClient.log(UtilClient.to_jsonstring(TeaCore.to_map(resp)))
	
	@staticmethod
	def pull_ip(self,RecordId) -> None:
		describe_domain_record_info_request = alidns_20150109_models.DescribeDomainRecordInfoRequest(
			record_id=RecordId
		)
		resp = self.client.describe_domain_record_info(describe_domain_record_info_request)
		return TeaCore.to_map(resp)["body"]["Value"]

	@staticmethod
	def Get_RecordId(self,sub_domain) -> None:
		describe_sub_domain_records_request = alidns_20150109_models.DescribeSubDomainRecordsRequest(
			sub_domain=sub_domain
		)
		resp = self.client.describe_sub_domain_records(describe_sub_domain_records_request)
		return TeaCore.to_map(resp)["body"]["DomainRecords"]["Record"][0]["RecordId"]

if __name__ == '__main__':
	#ipv4 = Moeip.Get_Ip("ipv4"))
	ipv6 = Moeip.Get_Ip("ipv6")
	client = Moeip(key.access_key_id, key.access_key_secret)
	RecordId = Moeip.Get_RecordId(client,key.domain)
	if ipv6 != Moeip.pull_ip(client,RecordId):
		Moeip.push_ip(client,RecordId,'test','AAAA',ipv6,600)
	else:
		print ("记录一致")
	
	#Moeip.push_ip(client,RecordId,'test','AAAA',"::0",600)

	
