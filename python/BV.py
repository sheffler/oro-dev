#
# Verilog 4-valued bitvector manipulation.
#  Internal representation is simple [01xz]+ string.
#


import re
import string
import types
import random

#
# Verilog string format is
#  [size]'[base][string]
# base is b (binary), o (octal) or h (hex).
#

_sizepat_ = "(?:\d+)?"
_basepat_ = "[bBoOhH]"
_numbpat_ = "[0-9abcdefABCDEFxXzZ_]+"

#
# Pattern to match Verilog string
#
_vpat_ = "(%s)'(%s)(%s)$" % (_sizepat_, _basepat_, _numbpat_)
_cpat_ = re.compile(_vpat_)

_illegalVerilogPat_ = "Illegal verilog string: %s"

#
# This pattern determines if this is a raw "01zx" string
#
_rawpat_ = "[01zx]+$"
_crawpat_ = re.compile(_rawpat_)

#
# Parse verilog bit string and convert to cononical internal form.
#
def _parse_verilog(s):

    mat = _cpat_.search(s)

    if not mat:
	raise _illegalVerilogPat_ % (s)

    (size, base, numb) = mat.groups()

    if size == "":
	size = 32			# default bit size
    else:
	size = string.atoi(size)	# to integer

    numb = string.lower(numb)

    res = ""

    if base in "bB":
	subst = ["0", "1"]
	xsubst = "x"
	zsubst = "z"
	maxd = 1

    if base in "oO":
	subst = ["000", "001", "010", "011",
		 "100", "101", "110", "111"]
	xsubst = "xxx"
	zsubst = "zzz"
	maxd = 7

    if base in "hH":
	subst = ["0000", "0001", "0010", "0011",
		 "0100", "0101", "0110", "0111",
		 "1000", "1001", "1010", "1011",
		 "1100", "1101", "1110", "1111"]
	xsubst = "xxxx"
	zsubst = "zzzz"
	maxd = 15

    for n in numb:
	if n == "_":
	    pass
	elif n == "x":
	    res = res + xsubst
	elif n == "z":
	    res = res + zsubst
	else:
	    i = string.atoi(n, maxd+1)	# choose correct base
	    if (i > maxd):
		raise _illegalVerilogPat_ % (s)
	    res = res + subst[i]

    # Sign-extend string if shorter than size
    if (len(res) < size):
	missing = size - len(res)
	xtend = res[0]			# msb
	res = (xtend * missing) + res

    # If string is larger than size, truncate
    if (len(res) > size):
	res = res[-size:]
    
    return res



#
# This class is used internally to indicate to BV that the initializer
# need not be parsed.
#
class __BVinit__:

    def __init__(self, val):

	if type(val) != types.StringType:
	    raise "illegal initializer %s" % val

	self.repr = val
	return

#
# Bit Vector Class - implements 4-valued logic and operations
#
#  CONSTRUCTOR
#    from: int, verilog string, 4-valued string, BV
#
#  OPS:
#    BV[1] subscript - returns a single character: '0', '1', 'x', 'z'
#    BV[2:0] range - returns another BV (BV[2:2] returns one bit BV)
#    BV + BV - concatenation
#    BV * n  - replication
#    BV | BV - bitwise OR
#    BV & BV - bitwise AND
#    BV ^ BV - bitwise XOR
#    ~BV - bitwise inversion (0->1, 1->0, x->x, z->x)
#    BV >> int - right shift (0 padded)
#    BV << int - left shift  (0 padded)
#
#    int(BV) - convert to an int
#    long(BV) - convert to a long
#
#  METHODS:
#    cmp(BV) - compare this BV with an 'expect' BV
#    eql(BV) - strict string equality
#
#    rand()    - generate rand two-valued BV of same length
#    randne()  - generate rand two-valued BV not equal to self
#    randx()   - generate rand three-valued BV of same length
#    randxne() - generate rand three-valued BV not equal to self
#
#    bit(n) - bit extraction as single character string (not a BV)
#    subst(hi, lo, BV) - return new BV with bits substituted
#
#  PRINTING/CONVERSION
#    vloghex() - Verilog hex string representation
#    vlogbin() - Verilog binary string representation
#
class BV:

    #
    # Constructor
    #  integer		-> 32 bit bitstring
    #  integer, N       -> N-bit bitstring
    #  "4'b10xz"	-> verilog bitstring, canonical 1 bit per char
    #                      (also supports 'o and 'h formats)
    #  "01xz..."        -> raw string, for user.  Regexp pat '[01zx]+'
    #  __BVinit__	-> raw string, used internally
    #
    def __init__(self, val, size=32):

        if isinstance(val, BV):
            self.repr = val.repr

        elif isinstance(val, __BVinit__):
            self.repr = val.repr

        elif type(val) == types.IntType or type(val) == types.LongType:
	    repr = ""
	    for i in range(size):
		bitval = val & (0x1L << size-1-i)
		if bitval == 0:
		    repr = repr + '0'
		else:
		    repr = repr + '1'
	    self.repr = repr

	elif type(val) == types.StringType:
            if _crawpat_.match(val):
                # If raw "[01zx]+" string ... don't parse as Verilog
                self.repr = val
            else:
                # else, parse as verilog
                self.repr = _parse_verilog(val)
        else:
            raise "Illegal initializer %s for bitvector." % str(val)


    #
    # Selection
    #  single bit [0] - result is single char
    #  range of bits [3:0] - result is BV
    #  range of bits [0:2] is illegal and raises exception
    #
    def __getitem__(self, pos):

	if type(pos) == types.SliceType:

	    start = pos.start		# greater
	    stop = pos.stop		# smaller
	    step = pos.step

	    if step != None:
		raise "stepsize not implemented"

	    if stop > start:
		raise "illegal slice %s" % pos
	    
	    if pos.stop == 0:
		x = self.repr[-start-1 :]
	    else:
		x = self.repr[-start-1 : -stop]
		
	    return BV(__BVinit__(x))

	else:
	    return self.repr[-pos-1]

    #
    # Select single bit
    #
    def bit(self, pos):

	return self.repr[-pos-1]

    #
    # Substitute a BV for a slice and return the result.
    #
    # example:
    #   x = BV("8'bxxxxxxxx")
    #   x.subst(3, 0, BV("4'b0101")) -> "8'bxxxx0101"
    #
    def subst(self, vhi, vlo, y):

	lens = len(self.repr)
	leny = len(y.repr)

	if ((vhi - vlo + 1) != leny):
	    raise ("Size of substitution (%d) does not match slice (%d,%d)" %
		   (leny, vhi, vlo))

	start = lens - vhi - 1		# python string start
	end = lens - vlo		# python string end

	oldstr = self.repr
	newstr = oldstr[:start] + y.repr + oldstr[end:]

	return BV(__BVinit__(newstr))

    #
    # Concatenation - result is a BV
    #
    def __add__(self, y):
	return BV(__BVinit__(self.repr + y.repr))

    #
    # Multiplication - BV * int - result is replicated
    #
    def __mul__(self, n):

	if type(n) != types.IntType and type(n) != types.LongType:
	    raise "BV * n - RHS must be INT or LONG - not %s" % n

	return BV(__BVinit__(self.repr * n))
	

    #
    # Return verilog hex bit string
    #
    def vloghex(self):

	s = self.repr
	prefix = "%d'h" % len(self.repr)
	res = ""
	while len(s) != 0:
	    x = s[-4:]			# get the last four bits
	    s = s[:-4]			# the front of the string

	    if string.find(x, "x") != -1:
		digit = "x"
	    elif string.find(x, "z") != -1:
		digit = "z"
	    else:
		digit = "0123456789abcdef"[int(x, 2)]

	    res = digit + res

	return prefix + res

    #
    # Return Verilog binary string
    #
    def vlogbin(self):
	return "%d'b%s"% (len(self.repr), self.repr)

    #
    # Return [01xz]+ representation
    #
    def rawbin(self):
        return self.repr                # current internal representation is this

    #
    # Return size in number of bits
    #
    def size(self):
        return len(self.repr)

    #
    # Parsable string representation
    #
    def __repr__(self):
	return 'BV("%s")' % self.repr

    #
    # Integer - ex. int(bv)
    #
    def __int__(self):
	return string.atoi(self.repr, 2)

    #
    # Long - ex. long(bv)
    #
    def __long__(self):
	return string.atol(self.repr, 2)
    
    #
    # Bitwise or helper function.  ("wor" in verilog book)
    #
    def __orbitwise__(self, x, y):

	if x == 'z':
	    return y
	if y == 'z':
	    return x
	if x == '1' or y == '1':
	    return '1'
	if x == 'x' or y == 'x':
	    return 'x'
	return '0'

    #
    # Bitwise and helper function. ("wand" in verilog book)
    #
    def __andbitwise__(self, x, y):

	if x == '0' or y == '0':
	    return '0'
	if x == 'x' or y == 'x':
	    return 'x'
	if x == 'z' and y == 'z':
	    return 'z'
	return '1'

    #
    # Bitwise xor.  Truth table from Cver.
    #
    def __xorbitwise__(self, x, y):

        if x == '0' and y == '0':
            return '0'
        elif x == '0' and y == '1':
            return '1'
        elif x == '1' and y == '0':
            return '1'
        elif x == '1' and y == '1':
            return '0'
        else:
            return 'x'


    #
    # | - bitwise OR operator
    #
    def __or__(self, y):

	if len(self.repr) != len(y.repr):
	    raise "mismatched lengths: %s %s" % (self, y)
	
	r = map(lambda x,y,s=self: s.__orbitwise__(x,y),
		list(self.repr),
		list(y.repr))

	return BV(__BVinit__(string.join(r, '')))

    #
    # & - bitwise AND operator
    #
    def __and__(self, y):

	if len(self.repr) != len(y.repr):
	    raise "mismatched lengths: %s %s" % (self, y)
	
	r = map(lambda x,y,s=self: s.__andbitwise__(x,y),
		list(self.repr),
		list(y.repr))

	return BV(__BVinit__(string.join(r, '')))

    #
    # Invert helper function.
    #
    def __notbitwise__(self, x):
        if x == '0':
            return '1'
        elif x == '1':
            return '0'
        else:
            return 'x'

    #
    # ~ - bitwise inversion operator
    #
    def __invert__(self):

        s = map(lambda x: self.__notbitwise__(x),
                list(self.repr))

        return BV(__BVinit__(string.join(s, '')))
        
    #
    # ^ - bitwise XOR operator
    #
    def __xor__(self, y):

	if len(self.repr) != len(y.repr):
	    raise "mismatched lengths: %s %s" % (self, y)
	
	r = map(lambda x,y,s=self: s.__xorbitwise__(x,y),
		list(self.repr),
		list(y.repr))

	return BV(__BVinit__(string.join(r, '')))
		

    #
    # >> - right shift (padded with 0)
    #
    def __rshift__(self, n):


	if type(n) != types.IntType:
	    raise "Shift amount must be integer: %d" % n

	padding = "0" * n
	return BV(__BVinit__(padding + self.repr[:-n]))

    #
    # << - left shift (padded with 0)
    # 
    def __lshift__(self, n):
	
	if type(n) != types.IntType:
	    raise "Shift amount must be integer: %d" % n

	padding = "0" * n
	return BV(__BVinit__(self.repr[n:] + padding))

    #
    # rand - generate random two-valued BV of the same length
    #
    def rand(self):

	length = len(self.repr)

	charlist = map(lambda x: random.choice(['0', '1']), range(length))
	return(BV(__BVinit__(string.join(charlist, ''))))

    #
    # randne - generate two-valued BV not equal to this one
    #
    def randne(self):

	x = self.rand()
	while cmp(self.repr, x.repr) == 0:
	    x = self.rand()
	return x

    #
    # randx - generate random three-valued BV of the same length
    #
    def randx(self):

	length = len(self.repr)

	charlist = map(lambda x: random.choice(['0', '1', 'x']), range(length))
	return(BV(__BVinit__(string.join(charlist, ''))))
		

    #
    # randne - generate three-valued BV not equal to this one
    #
    def randxne(self):

	x = self.randx()
	while cmp(self.repr, x.repr) == 0:
	    x = self.randx()
	return x


    #
    # Helper functions for cmp
    #
    def __cmpreduce__(self, cum, next):
        return cum & next

    def __cmpbitwise__(self, act, exp):
        if exp == '0':
            if act == '0':
                return 1
            else:
                return 0
        elif exp == '1':
            if act == '1':
                return 1
            else:
                return 0
        elif exp == 'x':
            return 1
        else:
            return 0
            

    #
    # Compare this BV with an "expect" value
    #  expect pattern rules are:
    #   0/1 must compare with 0/1
    #   x is a don't care
    #   z doesn't match anything
    #
    def cmp(self, expect):

        assert(isinstance(expect, BV))

        return reduce(
            self.__cmpreduce__,
            map(lambda x, y: self.__cmpbitwise__(x, y),
                list(self.repr),
                list(expect.repr)
                ))

    #
    # Compare this BV character for character with another.
    #
    def eql(self, other):

        assert(isinstance(other, BV))
        return (cmp(self.repr, other.repr) == 0)




#
# BV Constants
#

BV0 = BV("1'b0")
BV1 = BV("1'b1")
BVX = BV("1'bx")
BVZ = BV("1'bz")

