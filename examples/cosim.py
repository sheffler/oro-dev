
from oroboro import *

def testtask():

  clk_sig = signal("top.clk")
  val_sig = signal("top.value")
  i = 10

  while 1:
    yield posedge(clk_sig)
    print "PY: Setting 'value' to %d" % i
    val_sig.set(BV(i))
    i = i + 10

def mainfn(tf):
  taskmsg("Starting Python Task")
  traceoff()
  t = task(testtask)

  yield timeout(0)
  return
