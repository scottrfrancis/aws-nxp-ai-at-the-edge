#!/bin/bash

LED=/sys/class/pwm/pwmchip4
PERIOD=10000000
DUTY=10000000

[[ ! -z $1 ]] && DUTY=$(( $PERIOD*$1/100 ))
[[ ! -d "${LED}/pwm0" ]] && echo 0 > $LED/export


echo 0 > $LED/pwm0/enable
echo $PERIOD > $LED/pwm0/period
echo $DUTY > $LED/pwm0/duty_cycle
echo 1 > $LED/pwm0/enable
