#
# Make a text window to write into
#

import tkserver
import string

from apvm import *

class client(systf):


    def soscb(self):

	# make our client part
	self.host = self.my_config_param_string("host")
	self.client = tkserver.windowClient(self.host)

	self.win = self.my_config_param_string("win")

	# use this format later
	self.iformat = pack_s_vpi_value(vpiIntVal, 0)

    def calltf(self):

	(fmt, i) = get_value_like(self.vobjs[0], self.iformat)
	msg = "%s %d\n" % ("Hello!", i)
	self.client.write(self.win, msg)
	return 1

class sleep(systf):

    def calltf(self):
	import time
	time.sleep(1)
	return 1





	



