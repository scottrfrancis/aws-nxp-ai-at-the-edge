#!/bin/bash

LED=/sys/class/pwm/pwmchip4

echo 0 > $LED/pwm0/enable
