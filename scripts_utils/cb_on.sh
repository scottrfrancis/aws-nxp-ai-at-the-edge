#!/bin/bash

CB=/sys/class/pwm/pwmchip3
PERIOD=10000000
DUTY=10000000

[[ ! -z $1 ]] && DUTY=$(( $PERIOD*$1/100 ))
[[ ! -d "${CB}/pwm0" ]] && echo 0 > $CB/export


echo 0 > $CB/pwm0/enable
echo $PERIOD > $CB/pwm0/period
echo $DUTY > $CB/pwm0/duty_cycle
echo 1 > $CB/pwm0/enable
