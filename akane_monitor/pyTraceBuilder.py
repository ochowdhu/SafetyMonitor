#/usr/bin/python
# take an Omar single point trace and make a csv out of it

import sys
import csv

PERIOD = 1

PERIOD = int(sys.argv[1])
vars = sys.argv[2].split(",")
vars.insert(0,'time')

if (len(sys.argv) > 4):
	outfile = open(sys.argv[3],'w+')
	inT = sys.argv[4]
else:
	outfile = sys.stdout
	inT = sys.argv[3]

print "got varlist: %s" % vars
print "writing CSV..."
dr = csv.DictWriter(outfile, vars)
dr.writeheader()
# fake it, no writeheader() in python 2.6
#for i in vars:
#	outfile.write(i + ",")
#outfile.write("\n")

inTrace = inT.split(";")
time = 0
for t in inTrace:
	# initialize row
	d = dict.fromkeys(vars, 0) 
	# fill in time
	d['time'] = time 
	# update based on given trace
	for s in t.split(','):
		for v in s:
			d[v] = 1
	print "writing d: %s" % d
	dr.writerow(d)
	time = time + PERIOD

print "Done writing csv..."
