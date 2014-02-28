#!/bin/python

# Take ANTLR4 parse tree and return an AST how I want it
#

# Rules to abstract:
#	only expr, prop can have one child, remove any other single child nodes	
#	remove symbols ("!" from nprop, "->" etc from expressions, parenthesis, etc
#	
#

import sys
import re

def ASTreduce(tree):
	#print "Running TEST( %s )" % (tree,)
	# Remove single child nodes that aren't expr or proposition -- Do this first
	if (len(tree) == 2):
		if (tree[0] == 'exp' or tree[0] == 'prop'):
			#print "hit exp or prop"
			return [tree[0], ASTreduce(tree[1])]
		else: 
			#print "length is two, but not exp or prop"
			return ASTreduce(tree[1]) 
	# Now extra nodes are gone, so this is all cleanup
	#### CLEANUP

	# get rid of not label on nprop's
	if (tree[0] == 'nprop'):
		#print "in nprop"
		return [tree[0], ASTreduce(tree[-1])]
	# base case -- not a list means we hit a prop label
	if (not isinstance(tree, list)):
		#print "Not instance, ending recursion"
		return tree	
	else:	# got something real, do some abstraction/cleanup
		#print "got non-Length 2 thing, cleanup..."
		if (tree[0] == "andprop" or tree[0] == "orprop" or tree[0] == "impprop"):
			return [tree[0], ASTreduce(tree[1]), ASTreduce(tree[-1])]
		elif (tree[0] == "notprop"):
			return [tree[0], ASTreduce(tree[2])]
		elif (tree[0] == "eventprop" or tree[0] == "alwaysprop" or tree[0] == "onceprop" or tree[0] == "palwaysprop"):
			return [tree[0], tree[1], tree[2], ASTreduce(tree[3])]	# return [prop, bound1, bound2, formula]
		elif (tree[0] == "sinceprop" or tree[0] == "untilprop"):
			return [tree[0], tree[2], tree[3], ASTreduce(tree[1]), ASTreduce(tree[4])]
		else:
			#print "Something that doesn't fit"
			exit(1)

if len(sys.argv) != 2:
	#print "Bad Input, Usage: python parse2ast.py <parsetree>"
	#print "where <parsetree> is lisp style parse tree string (enclosed in quotation marks)"
	inStr = sys.stdin.read()
	print "got %s from stdin" % (inStr,)
else:
	inStr = sys.argv[1]

# first remove commas
inStr = inStr.replace(' ,', '')
# remove temporal bounds
inStr = inStr.replace(' [[', '')
inStr = inStr.replace(' ]]', '')
inStr = inStr.replace(' <<', '')
inStr = inStr.replace(' >>', '')
inStr = inStr.replace(' [', '')
inStr = inStr.replace(' ]', '')
inStr = inStr.replace(' <', '')
inStr = inStr.replace(' >', '')
inStr = inStr.replace(' $$', '')
inStr = inStr.replace(' $', '')
# remove parenthesis (only order of ops ones)
inStr = inStr.replace(' ( ', ' ')
inStr = inStr.replace(' )', '')
# convert lisp struct to python list
inStr = inStr.replace('(', '[')
inStr = inStr.replace(')', ']')
# put name labels in parenthesis
inStr = re.sub('[a-zA-Z\&\|\-\>\~][a-zA-Z0-9\&\|\-\>\~]*', "'\g<0>'", inStr)
print "before commas:::: %s" % (inStr,)
# add commas to struct
inStr = re.sub(' ', ', ', inStr)
print "Using %s" % (inStr,)

#sys.exit(0)
inTree = eval(inStr)

print "Using tree %s" % (inTree,)

print "Reducing input..."

out = ASTreduce(inTree)
print "Reduced, new tree is:\n==============\n %s" % (out,)

