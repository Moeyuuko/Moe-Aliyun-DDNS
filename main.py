#!python3
#-*- coding:utf-8 -*-

import requests
import traceback

import re
import logging
import logging.handlers
from logging.handlers import TimedRotatingFileHandler
from logging.handlers import RotatingFileHandler

from typing import List
from Tea.core import TeaCore

from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_console.client import Client as ConsoleClient
from alibabacloud_tea_util.client import Client as UtilClient

import Config

#日志配置
LogLevel = Config.LogLevel
LogName = 'Moe-DDNS.log'
LogFormat = '[%(asctime)s %(filename)s] [%(levelname)s] %(message)s'

log_fmt = LogFormat
datefmt= '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(log_fmt,datefmt)

log_file_handler = TimedRotatingFileHandler(
	filename=LogName,
	when="D",
	interval=1,
	backupCount=Config.LogRetentionDays)
log_file_handler.suffix = "%Y-%m-%d_%H-%M.log"
log_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
log_file_handler.setFormatter(formatter)

logging.basicConfig(level=LogLevel,
	format=LogFormat,
	datefmt=datefmt,
#	filename=LogName,
	filemode='a')
log = logging.getLogger()
log.addHandler(log_file_handler)

# logging.basicConfig(level=LogLevel,
# 	format='[%(asctime)s %(filename)s] [%(levelname)s] %(message)s',
# 	datefmt='%Y-%m-%d %H:%M:%S',
# 	filename=LogName,
# 	filemode='a')

# console = logging.StreamHandler()
# console.setLevel(LogLevel)
# formatter = logging.Formatter('[%(levelname)s] %(message)s')
# console.setFormatter(formatter)
# logging.getLogger('').addHandler(console)

class Sample:
	def __init__(self):
		pass

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
		# 访问的域名 https://next.api.aliyun.com/product/Alidns#endpoint
		config.endpoint = f'alidns.cn-shenzhen.aliyuncs.com'
		return Alidns20150109Client(config)

class Moeip:
	def __init__ (self, access_key_id: str,access_key_secret: str):
		self.client = Sample.create_client(access_key_id, access_key_secret)
	
	def Requests_Url_Text(url):
		r = requests.get(url)
		return r.text

	def Get_Ip(Type = "ipv4"):
		if Type == "ipv6":
			return Moeip.Requests_Url_Text('http://ipv6-ip.moeyuuko.com/')
		elif Type == "ipv4":
			return Moeip.Requests_Url_Text('http://ipv4-ip.moeyuuko.com/')
	
	def push_ip(self,RecordId,rr,type,value,ttl=600) -> None:
		update_domain_record_request = alidns_20150109_models.UpdateDomainRecordRequest(
			record_id=RecordId,
			rr=rr,
			type=type,
			value=value,
			ttl=ttl
		)
		resp = self.client.update_domain_record(update_domain_record_request)
		#ConsoleClient.log(UtilClient.to_jsonstring(TeaCore.to_map(resp)))\
		return resp
	
	def pull_ip(self,RecordId) -> None:
		describe_domain_record_info_request = alidns_20150109_models.DescribeDomainRecordInfoRequest(
			record_id=RecordId
		)
		resp = self.client.describe_domain_record_info(describe_domain_record_info_request)
		return TeaCore.to_map(resp)["body"]["Value"]

	def Get_Record_Info(self,sub_domain) -> None:
		describe_sub_domain_records_request = alidns_20150109_models.DescribeSubDomainRecordsRequest(
			sub_domain=sub_domain
		)
		resp = self.client.describe_sub_domain_records(describe_sub_domain_records_request)
		#print (str(resp))
		return TeaCore.to_map(resp)

def main():
	if (Config.iptype == "ipv4"):
		ipvx = Moeip.Get_Ip("ipv4")
		DRtype = 'A'	##Domain Resolution Type
	elif (Config.iptype == "ipv6"):
		ipvx = Moeip.Get_Ip("ipv6")
		DRtype = 'AAAA'
	
	client = Moeip(Config.access_key_id, Config.access_key_secret)
	RecordId = Moeip.Get_Record_Info(client,Config.domain)["body"]["DomainRecords"]["Record"][0]["RecordId"]
	RecordRR = Moeip.Get_Record_Info(client,Config.domain)["body"]["DomainRecords"]["Record"][0]["RR"]
	ipvx_pull = Moeip.pull_ip(client,RecordId)

	if ipvx != ipvx_pull:
		re = Moeip.push_ip(client,RecordId,RecordRR,DRtype,ipvx,600)
		logging.debug (re)
		logging.info ("解析刷新 "+ipvx)
	else:
		logging.info ("解析一致 "+ipvx_pull)

if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		logging.error (e)
		#print(traceback.format_exc())

	
