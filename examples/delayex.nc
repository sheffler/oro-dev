#!/bin/csh

setenv PYTHONPATH .:../python

ncverilog +ncaccess+rwc +loadvpi=../src/libapvmvpi:apvm_startup -v apvm_delay.v delayex.v


