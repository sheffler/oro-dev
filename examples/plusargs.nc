#!/bin/csh

setenv PYTHONPATH .:../python

ncverilog +loadvpi=../src/libapvmvpi:apvm_startup +option1=value1 +flag1 -f plusargs.f plusargs.v 

