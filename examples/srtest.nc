#!/bin/csh

setenv PYTHONPATH .:../python

ncverilog +ncaccess+rwc +loadvpi=../src/libapvmvpi:apvm_startup +sr1:file=srtest.sr +sr1:debug=1 srtest.v 

