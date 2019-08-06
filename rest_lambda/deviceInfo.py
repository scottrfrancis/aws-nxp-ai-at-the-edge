#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

import subprocess
import json

class DeviceInfo:
	def __init__(self):
		self.__temperature = 0.0
		self.__cpu = 0
		self.__memory = 0
		self.__gpu = 0

	def __bashCommand(self, cmd):
		process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
		output, error = process.communicate()
		if error:
			raise Exception(error)
		return output

	def getCPUCoresCount(self):
		# check how many cpus we have
		cpuJson = self.__bashCommand("lscpu -J")
		lscpu = json.loads(cpuJson)
		cores = int(lscpu["lscpu"][7]["data"])
		return cores

	def getTemperature(self, index):
		# check how many cpus we have
		cores = self.getCPUCoresCount()
		# check out of the cores
		if index >= cores:
			raise Exception("We have " + str(cores) + " cores but temperature of core " + str(index) + " are requested")
		# get from the index
		f = open("/sys/class/thermal/thermal_zone" + str(index) +  "/temp", "r")
		temp = int(f.read())
		# kernel int to float
		self.__temperature = float(temp) / 1000.0
		return self.__temperature
