#!/bin/csh

setenv PYTHONPATH .:../python

ncverilog +loadvpi=../src/libapvmvpi:apvm_startup checker.v
