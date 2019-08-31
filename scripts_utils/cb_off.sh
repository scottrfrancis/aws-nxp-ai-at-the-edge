#!/bin/bash

CB=/sys/class/pwm/pwmchip3

echo 0 > $CB/pwm0/enable
