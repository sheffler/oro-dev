#!/bin/csh

# for linux
# setenv TK_LIBRARY /usr/lib/tk8.3/

setenv PYTHONPATH .:../python:

# Start a server
python tkserver.py >& SERVEROUT &

# give it some time to start
sleep 2

# Start one Verilog - send its output to "win1"
ncverilog +loadvpi=../src/libapvmvpi:apvm_startup +tkserver:host=localhost +tkserver:win=win1 tkserverdemo.v &

# Give the first one a head start
sleep 1

# Start another Verilog - send its output to "win2"
ncverilog +loadvpi=../src/libapvmvpi:apvm_startup +tkserver:host=localhost +tkserver:win=win2 tkserverdemo.v &





