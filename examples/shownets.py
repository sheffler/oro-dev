#
# Single arg to systf must be a module
#
#   res = $apvm("", "shownets", "shownets", top);
#


from apvm import *

import string
import pprint


class shownets(systf):

    # check validity of vobjs[0]
    def soscb(self):

	argtype = get(vpiType, self.vobjs[0])
	if (argtype != vpiModule):
	    raise "Arg0 to $shownets must be module instance"

    def calltf(self):

	fmt1 = "%g"

	# get current time
	tfmt = pack_s_vpi_time(vpiScaledRealTime, 0, 0, 0.0)
        # TOM: changed the handle for Icarus (3/13/04)
	# (fmt, lo, hi, rtime) = get_time_like(self.systf, tfmt)
	(fmt, lo, hi, rtime) = get_time_like(self.vobjs[0], tfmt)

	# get our module name
	modulename = get_str(vpiName, self.vobjs[0])
	vpi_print("\nPrinting nets for '%s' at time %2.2g:\n" % (modulename, rtime))

	# iterate through the nets printing their values
	net_iterator = iterate(vpiNet, self.vobjs[0])
	if net_iterator == None:
	    vpi_print("No nets found in this module")
	else:
	    net_h = scan(net_iterator)
	    format = pack_s_vpi_value(vpiBinStrVal, "")
	    while net_h != None:
		netname = get_str(vpiName, net_h)
		(fmt, strval) = get_value_like(net_h, format)
		vpi_print(" net %-10s  value is %s (binary)\n" % (netname, strval))
		net_h = scan(net_iterator)
	    vpi_print("\n")

	return 0

	

