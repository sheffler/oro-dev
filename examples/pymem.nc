#!/bin/csh

setenv PYTHONPATH .:../python

ncverilog +ncaccess+rwc +loadvpi=../src/libapvmvpi:apvm_startup pymem.v 

