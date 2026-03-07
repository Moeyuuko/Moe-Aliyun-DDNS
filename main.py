#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import logging
import requests
from logging.handlers import TimedRotatingFileHandler

from Tea.core import TeaCore
from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models

import Config

# 日志配置
LogLevel = Config.LogLevel
LogName = 'Moe-DDNS.log'
LogFormat = '[%(asctime)s %(filename)s] [%(levelname)s] %(message)s'
datefmt = '%Y-%m-%d %H:%M:%S'

formatter = logging.Formatter(LogFormat, datefmt)

log_file_handler = TimedRotatingFileHandler(
	filename=LogName,
	when="D",
	interval=1,
	backupCount=Config.LogRetentionDays)
log_file_handler.suffix = "%Y-%m-%d_%H-%M.log"
log_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")
log_file_handler.setFormatter(formatter)

logging.basicConfig(level=LogLevel, format=LogFormat, datefmt=datefmt, filemode='a')
log = logging.getLogger()
log.addHandler(log_file_handler)


class Moeip:
	def __init__(self, access_key_id: str, access_key_secret: str):
		config = open_api_models.Config(
			access_key_id=access_key_id,
			access_key_secret=access_key_secret
		)
		# 访问的域名 https://next.api.aliyun.com/product/Alidns#endpoint
		config.endpoint = 'alidns.cn-shenzhen.aliyuncs.com'
		self.client = Alidns20150109Client(config)

	@staticmethod
	def get_ip(ip_type="ipv4") -> str:
		logging.debug("==本机ip==")
		if ip_type == "ipv6":
			url = 'http://ipv6-ip.moeyuuko.com/'
		else:
			url = 'http://ipv4-ip.moeyuuko.com/'
		resp = requests.get(url, timeout=10)
		resp.raise_for_status()
		reip = resp.text.strip()
		logging.debug(reip)
		return reip

	def push_ip(self, record_id, rr, record_type, value, ttl=600):
		update_domain_record_request = alidns_20150109_models.UpdateDomainRecordRequest(
			record_id=record_id,
			rr=rr,
			type=record_type,
			value=value,
			ttl=ttl
		)
		resp = self.client.update_domain_record(update_domain_record_request)
		logging.debug(resp)
		return resp

	def pull_ip(self, domain, record_type):
		logging.debug("==拉取==")
		record_info = self.get_record_info(domain)
		records = record_info["body"]["DomainRecords"]["Record"]
		logging.debug(records)
		for record in records:
			if record['Type'] == record_type:
				reip = record['Value']
				reid = record['RecordId']
				rerr = record['RR']
				logging.debug("==远程记录==")
				logging.debug(reip)
				logging.debug(reid)
				logging.debug(rerr)
				return reip, reid, rerr
		raise ValueError(f"未找到域名 {domain} 的 {record_type} 记录")

	def get_record_info(self, sub_domain):
		describe_sub_domain_records_request = alidns_20150109_models.DescribeSubDomainRecordsRequest(
			sub_domain=sub_domain
		)
		resp = self.client.describe_sub_domain_records(describe_sub_domain_records_request)
		logging.debug(resp)
		return TeaCore.to_map(resp)


def execute(client: Moeip, iptype: str) -> None:
	if iptype == "ipv4":
		ipvx = Moeip.get_ip("ipv4")
		record_type = 'A'
	elif iptype == "ipv6":
		ipvx = Moeip.get_ip("ipv6")
		record_type = 'AAAA'
	else:
		raise ValueError(f"未知的 IP 类型: {iptype}")

	ipvx_pull, record_id, record_rr = client.pull_ip(Config.domain, record_type)

	if ipvx != ipvx_pull:
		resp = client.push_ip(record_id, record_rr, record_type, ipvx, Config.ttl)
		logging.debug(resp)
		logging.info("解析刷新 " + ipvx)
	else:
		logging.info("解析一致 " + ipvx_pull)


def main() -> None:
	client = Moeip(Config.access_key_id, Config.access_key_secret)
	if Config.iptype == "ipv4":
		execute(client, "ipv4")
	elif Config.iptype == "ipv6":
		execute(client, "ipv6")
	elif Config.iptype == "ipv4&6":
		execute(client, "ipv4")
		execute(client, "ipv6")


if __name__ == '__main__':
	try:
		main()
	except Exception as e:
		logging.error(e, exc_info=True)

