#
# Connectionless protocol 
# Server listens at port for single-line displays.
# Protocol is
#    win'message
# where ' is the \001 character.
#
# Tom Sheffler
# March 2004
#

import sys
print sys.path

import Tkinter
from ScrolledText import ScrolledText
import socket
import sys
import string

host = "localhost"
port = 4000
request_queue_size = 5


class windowServer:

    def __init__(self):

	self.windows = { }		# table of open windows

	# Make the root window with the quit button
	root = Tkinter.Tk()
	root.title("Tk Server")
	# root.minsize(1,1)

	quit_button = Tkinter.Button(root)
	quit_button['text'] = 'Quit TkServer'
	quit_button['command'] = self.quit
	quit_button.pack()

	# The window handler listens on this socket for display rqsts
	self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	self.socket.bind(("localhost", 4000))

	Tkinter.tkinter.createfilehandler(self.socket,
					  Tkinter.tkinter.READABLE,
					  self.readSocket)

	root.mainloop()

    def quit(self):

	print "Quitting TK Server.\n"
	sys.exit(0)

    def readSocket(self, sock, stateMask):

	print "Read Socket!"

	try:
	    (x, addr) = sock.recvfrom(1000) # max received
	    print "Read: ", addr, x
	    (win, msg) = string.split(x, "\001", 1)

	    # send this data to window win
	    self.display(win, msg)

	except socket.error, e:
	    print "recv failed:", e
	
    #
    # Display the message in window named win
    #
    def display(self, win, msg):

	w = self.findwin(win)
	w.insert(Tkinter.END, msg + "\n")
	w.yview_pickplace(Tkinter.END)


    #
    # See if we have a window named 'win', if so return it, else create
    #
    def findwin(self, win):

	if self.windows.has_key(win):
	    return self.windows[win]
	else:
	    neww = Tkinter.Tk()
	    neww.title(win)
	    w = ScrolledText(neww)
	    w.pack(expand=1, fill=Tkinter.BOTH)
	    w.insert(Tkinter.END, "New Window Named: %s\n" % win)
	    w.yview_pickplace(Tkinter.END)

	    self.windows[win] = w
	    return w


#
# This is the client class.  It simply opens a socket and writes to it.
#
class windowClient:

    def __init__(self, h=host):

	self.host = h
	self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def write(self, win, msg):

	if 0:
	    print "Write"

	text = win + "\001" + string.strip(msg)
	try:
	    bytes = self.socket.sendto(text, 0, (self.host, port))
	    if 0:
		print "Write Data:", bytes, text
	except socket.error, e:
	    print "Socket send failed:", e



def main():

    root = windowServer()



if __name__ == "__main__":

    main()

