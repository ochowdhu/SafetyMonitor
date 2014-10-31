## quick script to build a big formula

import sys

r= int(sys.argv[1])
for i in range(0,r):
	#print("<0,10>x{0:04x}\n".format(i)),
	print("x{0:04x}||x{1:04x}\n".format(i,i+1)),

