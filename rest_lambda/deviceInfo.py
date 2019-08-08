"""Apalis iMX8 Device Info class"""

#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

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

	def getRAMUsage(self):
		return psutil.virtual_memory().percent

	def getRAMTotal(self):
		return round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 4)

	def getRAMFree(self):
		return round(psutil.virtual_memory().free / 1024 / 1024 / 1024, 4)

	def getGPUMemoryUsage(self):
		#stuff = self.__bashCommand("cat /sys/kernel/debug/gc/meminfo | grep Used");
		#slices = stuff.split()
		#used = int(slices[2])
		#stuff = self.__bashCommand("cat /sys/kernel/debug/gc/meminfo | grep Free");
		#slices = stuff.split()
		#free = int(slices[2])
		#return (used * 100) / free
		return 0
