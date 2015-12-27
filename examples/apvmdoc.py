from apvm import *
import apvm
import pydoc

class apvmdoc(systf):

    def calltf(self):
        pydoc.help(apvm)
        return 1

