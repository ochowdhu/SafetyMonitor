## quick script to build a big mask.ini

import sys

r= int(sys.argv[1])
for i in range(0,r):
	print("#define MASK_x{0:04x} {0}".format(i))

