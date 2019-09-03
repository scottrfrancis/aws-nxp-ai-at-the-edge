"""Apalis iMX8 Device Ctrl class"""

#
# Copyright 2019 Toradex AG. or its affiliates. All Rights Reserved.
#

import subprocess
import json

__author__ = 'Leonardo Graboski Veiga'
__version__ = '0.0'
__license__ = ''
__copyright__ = 'Copyright 2019 Toradex AG'


class DeviceCtrl:
	def __init__(self):
		self.__cam_res = "640x480"
		self.__period = 10000000

		self.__cb_index = 3
		self.__cb_duty = self.__period

		self.__led_index = 4
		self.__led_duty = self.__period

		# Conveyor belt
		self.__export(self.__cb_index)
		self.__set_period(self.__cb_index, self.__period)
		self.set_cb_speed(100)

		# LED
		self.__export(self.__led_index)
		self.__set_period(self.__led_index, self.__period)
		self.set_led_brightness(100)

	def __writeToFile(self, file, cmdval):
		try:
			f = open(file, "w")
			f.write(cmdval)
			f.flush()
			f.close()
		except Exception as e:
			print("Could not write to file " + str(file) + "! " + repr(e))
			return 1
		else:
			return 0

	def __export(self, pwmchip):
		self.__writeToFile("/sys/class/pwm/pwmchip" + str(pwmchip) + "/export", "0")

	def __set_period(self, pwmchip, period):
		self.__writeToFile("/sys/class/pwm/pwmchip" + str(pwmchip) + "/pwm0/period", str(period))

	def __set_duty_cycle(self, pwmchip, duty):
		self.__writeToFile("/sys/class/pwm/pwmchip" + str(pwmchip) + "/pwm0/duty_cycle", str(duty))

	def __disable(self, pwmchip):
		self.__writeToFile("/sys/class/pwm/pwmchip" + str(pwmchip) + "/pwm0/enable", "0")

	def __enable(self, pwmchip):
		self.__writeToFile("/sys/class/pwm/pwmchip" + str(pwmchip) + "/pwm0/enable", "1")

	def __percent_boundaries(self, percentage):
		percentage = int(percentage)
		if percentage > 100:
			percentage = 100
		elif percentage < 0:
			percentage = 0
		pctg = int(percentage * self.__period / 100)
		return pctg

	def set_cb_speed(self, percentage):
		try:
			self.__cb_duty = self.__percent_boundaries(percentage)
			self.__disable(self.__cb_index)
			self.__set_duty_cycle(self.__cb_index, self.__cb_duty)
			if self.__cb_duty > 0:
				self.__enable(self.__cb_index)
		except Exception as e:
			print("Could not set cb speed! " + repr(e))
			return 1
		else:
			return 0


	def set_led_brightness(self, percentage):
		try:
			self.__led_duty = self.__percent_boundaries(percentage)
			self.__disable(self.__led_index)
			self.__set_duty_cycle(self.__led_index, self.__led_duty)
			if self.__led_duty > 0:
				self.__enable(self.__led_index)
		except Exception as e:
			print("Could not set LED brightness! " + repr(e))
			return 1
		else:
			return 0

	def get_cb_speed(self):
		return int(100 * self.__cb_duty / self.__period)

	def get_led_brightness(self):
		return int(100 * self.__led_duty / self.__period)