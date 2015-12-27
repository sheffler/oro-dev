#
# Show how to look for plusargs
#

from apvm import *

class plusargs(systf):


    def soscb(self):

	vpi_print("Sys Info: %s\n" % str(sim_info))

	x = plusarg_option("option1")
	vpi_print('Result of plusarg_option("option1"): %s\n' % x)

	x = plusarg_option("option2")
	vpi_print('Result of plusarg_option("option2"): %s\n' % x)

	x = plusarg_option("option3")
	vpi_print('Result of plusarg_option("option3"): %s\n' % x)

	x = plusarg_flag("flag1")
	vpi_print('Result of plusarg_flag("flag1"): %s\n' % x)

	x = plusarg_flag("flag2")
	vpi_print('Result of plusarg_flag("flag2"): %s\n' % x)

	x = plusarg_flag("flag3")
	vpi_print('Result of plusarg_flag("flag3"): %s\n' % x)


