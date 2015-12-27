
#
# An instance of a memory systf indicates a memory pool with
# a verilog object.  Its other arguments are address, data
# (verilog registers) and a command to perform on the pool:
# "get", "put", "dump", "load."  Commands that need additional
# arguments get them from additional arguments.
#

from apvm import *
import string

_debugging = 1

class mem(systf):

    _pools = { }			# hashed by verilog path
    _poolsaddrsize = { }
    _poolsdatasize = { }
    _poolsnames = { }

    def soscb(self):

	# how we identify our pool
	arg0 = self.vobjs[0]
	self.path = intern(get_str(vpiFullName, arg0))

	self.addr = self.vobjs[1]	# handle
	self.data = self.vobjs[2]	# handle

	self.addrsize = get(vpiSize, self.addr)
	self.datasize = get(vpiSize, self.data)

	self.checkpooladdrsize()
	self.checkpooldatasize()
	self.addpoolsname()

	self.cmd = self.vobjs[3]	# should be const or str valued

	if len(self.vobjs) > 4:
	    self.arg = self.vobjs[4]

	self.strformat = pack_s_vpi_value(vpiStringVal, "xx")

	vpi_print("        Mem attaching to pool: %s\n" % self.path)
	if not self._pools.has_key(self.path):
	    self._pools[self.path] = { }

    # do something to the addr - either intern it or long it
    def addr_intern(self, addrstring):
	# addrval = intern(addrval)
	addrval = long(addrstring, 2)	# good to hash
	return addrval

    def checkpooladdrsize(self):

	if self._poolsaddrsize.has_key(self.path):
	    oldsize = self._poolsaddrsize[self.path]

	    if self.addrsize != oldsize:
		raise "Pools address register sizes do not match"
	else:
	    self._poolsaddrsize[self.path] = self.addrsize

    
    def checkpooldatasize(self):

	if self._poolsdatasize.has_key(self.path):
	    oldsize = self._poolsdatasize[self.path]

	    if self.datasize != oldsize:
		raise "Pools data register sizes do not match"
	else:
	    self._poolsdatasize[self.path] = self.datasize

    # add our name to the list of instances using this pool
    def addpoolsname(self):

	if self._poolsnames.has_key(self.path):
	    pass
	else:
	    self._poolsnames[self.path] = [ ]

	self._poolsnames[self.path].append(self.name)
	self._poolsnames[self.path].sort()

    # util to determine the main "name" for this pool
    def mainname(self):

	l = self._poolsnames[self.path]
	return l[0]
    

    #
    # This is straightforward
    #

    def calltf(self):

	x = get_value_like(self.cmd, self.strformat)
	cmdstr = intern(x[1])
	if _debugging:
	    vpi_print("Mem CALLTF CMD: %s\n" % cmdstr)

	if cmdstr == "put":

	    addrbinstr = get_val_bin_str(self.addr)
	    ai = self.addr_intern(addrbinstr)

	    dataval = get_val_bin_str(self.data)

	    if _debugging:
		vpi_print("Mem Put: 0x%lx %s\n" % (ai, dataval))

	    self._pools[self.path][ai] = dataval
	    return 1

	elif cmdstr == "get":

	    addrbinstr = get_val_bin_str(self.addr)
	    ai = self.addr_intern(addrbinstr)

	    try:
		dataval = self._pools[self.path][ai]
		svp = pack_s_vpi_data(vpiBinStrVal, dataval)
		put_value(self.data, svp)
		return 1
	    except:
		return 0

	elif cmdstr == "dump":

	    x = get_value_like(self.arg, self.strformat)
	    filename = x[1]

	    if _debugging:
		vpi_print("Mem Dump: %s\n" % filename)

	    f = open(filename, "w")

	    pool = self._pools[self.path]
	    keys = pool.keys()
	    keys.sort()

	    for k in keys:
		data = pool[k]
		f.write("%0*lx %s\n" % (self.addrsize, k, data))
	    return 1
	    
	elif cmdstr == "load":

	    x = get_value_like(self.arg, self.strformat)
	    filename = x[1]
	    f = open(filename, "r")

	    pool = self._pools[self.path]

	    lines = f.getlines()
	    for l in lines:
		x = string.split(l)
		k = addr_hash(x[0])
		data = intern(x[1])
		pool[k] = data

	    return 1
	    
	else:
	    vpi_print("Memory command str '%s' not implemented" % cmdstr)
	    raise "Memory command str '%s' not implemented" % cmdstr

	    
    #
    # The save/restore mechanism is pretty simple, but we do have
    # to deal with the fact that multiple instances may attach to
    # the same pool.
    #

    def save_client_data(self):

	# pass

	# only one instance sharing pool should save
	if self.name == self.mainname():
	    self.save_data(self.path, self._pools[self.path])
	    
    def restore_client_data(self):
	
	if self.name == self.mainname():
	    self._pools[self.path] = self.restore_data(self.path)
	
