#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

import subprocess
import json

class Sensors:
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

	def getTemperature(self):
		# check how many cpus we have
		cpuJson = self.__bashCommand("lscpu -J")
		lscpu = json.loads(cpuJson)
		cores = int(lscpu["lscpu"][7]["data"])
		# we have to get the highest one
		temps = []
		for i in range(0, cores):
			f = open("/sys/class/thermal/thermal_zone" + str(i) +  "/temp", "r")
			temps.append(int(f.read()))
		temp = max(temps)
		self.__temperature = float(temp) / 1000.0
		return self.__temperature
