
#
# Clean up
#

clean:
	-rm *~
	(cd src; make clean)
	(cd doc; make clean)
	(cd python; make clean)
	(cd examples; make clean)



