#/usr/bin/python
# make a csv with different trace types

import sys
import csv

PERIOD = 1

PERIOD = int(sys.argv[1])
DURATION = int(sys.argv[2])

vars = ['time', 'allT', 'allF', 'alt1', 'perT3', 'perT10', 'perT100', 'perT1000', 'perT10000', 'perF3', 'perF10', 'perF100', 'perF1000', 'perF10000', 'burst5', 'burst50', 'burst500', 'burst5000']

if (len(sys.argv) > 3):
	outfile = open(sys.argv[3],'w+')
else:
	outfile = sys.stdout

#print "got varlist: %s" % vars
print "writing CSV..."
dr = csv.DictWriter(outfile, vars)
#dr.writeheader()
# fake it, no writeheader() in python 2.6
for i in vars:
	outfile.write(i + ",")
outfile.write("\n")

time = 0
lastAlt1 = True
burst5c = 0
b5val = False
burst50c = 0
b50val = False
burst500c = 0
b500val = False
burst5000c = 0
b5000val = False
for t in range(0,DURATION, PERIOD):
	# initialize row
	d = dict.fromkeys(vars, 0) 
	# fill in time
	d['time'] = t
	# init Trues
	d['allT'] = 1
	lastAlt1 = not lastAlt1 
	d['alt1'] = int(not lastAlt1)
	#update periodic trues
	# initialized 0, make 1 if time
	if (t % 3 == 0):
		d['perT3'] = 1
	if (t % 10 == 0):
		d['perT10'] = 1
	if (t % 100 == 0):
		d['perT100'] = 1
	if (t % 1000 == 0):
		d['perT1000'] = 1
	if (t % 10000 == 0):
		d['perT10000'] = 1
	# update periodic falses
	# initialized 0, make 1 if not time
	if (t % 3 != 0):
		d['perF3'] = 1
	if (t % 10 != 0):
		d['perF10'] = 1
	if (t % 100 != 0):
		d['perF100'] = 1
	if (t % 1000 != 0):
		d['perF1000'] = 1
	if (t % 10000 != 0):
		d['perF10000'] = 1

	if (burst5c >= 5):
		b5val = not b5val
		burst5c = 0
	if (burst50c >= 50):
		b50val = not b50val
		burst50c = 0
	if (burst500c >= 500):
		b500val = not b500val
		burst500c = 0
	if (burst5000c >= 5000):
		b5000val = not b5000val
		burst5000c = 0
	d['burst5'] = int(b5val)
	burst5c = burst5c + 1
	d['burst50'] = int(b50val)
	burst50c = burst50c + 1
	d['burst500'] = int(b500val)
	burst500c = burst500c + 1
	d['burst5000'] = int(b5000val)
	burst5000c = burst5000c + 1

	# update based on given trace
	dr.writerow(d)

print "Done writing csv..."
