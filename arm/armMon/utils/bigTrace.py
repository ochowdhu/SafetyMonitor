# quick script to build 1000 var traces

import sys
import csv

## outfile or to stdout
if (len(sys.argv) > 4):
	outfile = open(sys.argv[3], 'w+')
else:
	outfile = sys.stdout

r = int(sys.argv[1])
nsteps = int(sys.argv[2])

vars = []
for i in range(0,r):
	name = "x{0:04x}".format(i)
	vars.append(name)


dr = csv.DictWriter(outfile, vars);
#dr.writeheader()
# fake it, no writeheader() in python 2.6
for i in vars:
	outfile.write(i + ",")
outfile.write("\n")

d = dict.fromkeys(vars,0)

for i in range(0,nsteps):
	dr.writerow(d)
