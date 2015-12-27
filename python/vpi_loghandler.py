"""
A verilog VPI logging handler for use with the apvm api.

Contributed by T. Loftus.
"""

import string, logging, logging.handlers, types, apvm

class VPIHandler(logging.Handler):
    """
    A class whichreroutes log messages to the verilog VPI interface
    """
    def __init__(self):
        """
        Initialize the instance - really doesn't do anything right now
        """
        logging.Handler.__init__(self)

    def emit(self, record):
        """
        parse and send the record to the simulator logfile
        """
	try:
            msg = self.format(record) 
            apvm.vpi_print( "%s" % (msg))
		
        except:
            print "cant send record to logfile using python logging"


def main():
    sh = VPIHandler()
    logger = logging.getLogger("vpi_loghandler")
    fmt = logging.Formatter("%(asctime)s %(filename)s:%(lineno)d 
%(levelname)-5s - %(message)s")
    logger.setFormatter(fmt)
    logging.getLogger("").setLevel(logging.DEBUG)
    logger.propagate = 0
    logger.addHandler(sh)
    logger.info("testing testing %s testing", "one two three")
    logger.info("hello hello %s then", "whats all this")
    logger.removeHandler(sh)

if __name__ == "__main__":
    main()
