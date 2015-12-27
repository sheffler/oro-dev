from apvm import *
import apvm
import oroboro
import pydoc


class orodoc(systf):

    def calltf(self):
        # pydoc.help(oroboro)
        print "Starting Pydoc HTML Server."
        print "Point your browser as directed."
        pydoc.gui()
        return 1

