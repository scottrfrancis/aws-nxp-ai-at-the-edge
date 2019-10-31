"""Apalis iMX8 Device Info class"""

#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

import os.path as pcheck
import subprocess
import psutil
import json

__author__ = 'Matheus Castello'
__version__ = '0.0'
__license__ = ''
__copyright__ = 'Copyright 2019 Toradex AG'

#
# I try to make this more generic but the thermal zones depends on device tree
# descriptions, so this deviceInfo will be util only for the
# NXP® i.MX 8QuadMax (i.MX 8QM), 2x Arm® Cortex-A72, 4x Cortex-A53, 2x Cortex-M4
#

class DeviceInfo:
	def __init__(self):
		self.__cpu_a53_temperature = 0.0
		self.__cpu_a72_temperature = 0.0
		self.__gpu0_temperature = 0.0
		self.__gpu1_temperature = 0.0

		self.__serial_number = "00000000"
		self.__product_id = "0"
		self.__product_revision = "0"

		# Initial checks

		# /proc/device-tree symlinks to /sys/firmware/devicetree/base
		#self.DTDIR = '/proc/device-tree'
		self.DTDIR = '/sys/firmware/devicetree/base/'
		
		self.dtdir_exist = pcheck.isdir(self.DTDIR)

	def __bashCommand(self, cmd):
		process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		output, error = process.communicate()
		if error:
			raise Exception(error)
		return output

	def __getCelsiusFromThermalZone(self, index):
		# get from thermal zone
		f = open("/sys/class/thermal/thermal_zone" + str(index) + "/temp", "r")
		temp = int(f.read())
		# kernel int to float
		return float(temp) / 1000.0

	def getCPUCoresCount(self):
		# check how many cpus we have
		cpuJson = self.__bashCommand("lscpu -J")
		lscpu = json.loads(cpuJson)
		# get cpu cores and threads per core
		for i in range(0, len(lscpu["lscpu"])):
			if lscpu["lscpu"][i]["field"] == "CPU(s):":
				cores = int(lscpu["lscpu"][i]["data"])
			if lscpu["lscpu"][i]["field"] == "Thread(s) per core:":
				threads = int(lscpu["lscpu"][i]["data"])
		return int(cores / threads)

	def getTemperatureCPUA53(self):
		# get from thermal zone
		self.__cpu_a53_temperature = self.__getCelsiusFromThermalZone(0)
		return self.__cpu_a53_temperature

	def getTemperatureCPUA72(self):
		# get from thermal zone
		self.__cpu_a72_temperature = self.__getCelsiusFromThermalZone(1)
		return self.__cpu_a72_temperature

	def getTemperatureGPU0(self):
		# get from thermal zone
		self.__gpu0_temperature = self.__getCelsiusFromThermalZone(2)
		return self.__gpu0_temperature

	def getTemperatureGPU1(self):
		# get from thermal zone
		self.__gpu1_temperature = self.__getCelsiusFromThermalZone(3)
		return self.__gpu1_temperature

	def getCPUUsage(self):
		return psutil.cpu_percent()

	def getCPUUsageDetailed(self):
		return psutil.cpu_percent(percpu=True)

	def getRAMUsage(self):
		return psutil.virtual_memory().percent

	def getRAMTotal(self):
		return round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 4)

	def getRAMFree(self):
		return round(psutil.virtual_memory().free / 1024 / 1024 / 1024, 4)

	def getGPUMemoryUsage(self):
		stuff = self.__bashCommand("cat /sys/kernel/debug/gc/meminfo")
		print(stuff.split())
		slices = stuff.split()
		used = int(slices[9])
		slices = stuff.split()
		free = int(slices[21])
		return (used * 100) / free
		#return 0

	def getTdxSerialNumber(self):
		if self.dtdir_exist:
			with open(self.DTDIR + '/serial-number') as f:
				self.__serial_number = f.read().rstrip('\x00')
		return int(self.__serial_number)

	def getTdxProductID(self):
		if self.dtdir_exist:
			# Get SKU and module version
			with open(self.DTDIR + '/toradex,product-id') as f:
				self.__product_id = f.read().rstrip('\x00')
			try: # try to decode a number to an actual human readable info
				self.__product_id = self._module_info_decode(int(self.__product_id)) 
			except AttributeError:
				pass  # just provide 'undefined'
		return self.__product_id


	def getTdxProductRevision(self):
		if self.dtdir_exist:
			with open(self.DTDIR + '/toradex,board-rev') as f:
				self.__product_revision = f.read().rstrip('\x00')
		return self.__product_revision
