#!/usr/bin/python
##
##
## @author Aaron Kane
##
## Pulling some utility functions into a module to use across monitor algorithms

## Some constants
EXP_T, PROP_T, NPROP_T, NOT_T, AND_T, OR_T, IMPLIES_T, EVENT_T, ALWAYS_T, UNTIL_T, PALWAYS_T, PEVENT_T, SINCE_T, VALUE_T, INVALID_T = range(15)

TAGi, FORMULAi, DELAYi, VALIDi, LISTi, FLISTi = range(0,6) 

ALC_ALIVE, ALC_VIOLATE, ALC_SATISFY = range(0,3)
ALG_RES, ALG_STCONS, ALG_PURECONS, ALG_FSTCONS, ALG_RESCONS, ALG_ASTCONS, ALG_ARES, ALG_AIRES, ALG_IRES = range(0,9)

## debug constants
DBG_ERROR = 0x01
DBG_STRUCT = 0x02
DBG_SMON = 0x04
DBG_STATE = 0x08
DBG_TIME = 0x10
DBG_SAT = 0x20
#DBG_MASK = DBG_ERROR | DBG_STRUCT | DBG_SMON | DBG_STATE 
#DBG_MASK = DBG_ERROR | DBG_TIME | DBG_SMON | DBG_STRUCT | DBG_SAT
DBG_MASK = DBG_ERROR | DBG_TIME | DBG_SAT | DBG_SMON | DBG_STRUCT

# global constants
PERIOD = 1
sTag = 0


def setDBG_MASK(val):
	global DBG_MASK
	DBG_MASK = val
def setPeriod(per):
	global PERIOD
	PERIOD = per
class ipstructure:
	def __init__(self, tag, formula=[], delay=0):
		self.tag = tag
		self.formula = formula
		self.delay = delay
		self.history = []
		self.residues = []
		self.valid = 0

	def addHist(self, time, val):
		if (val):
			added = False
			for i in self.history:
				if i.extendedBy(time):
					i.addEntry(time)
					added = True
			if (not added):
				self.history.append(Interval(time, time+PERIOD))
		# Add to validity whether True or false
		self.valid = max(self.valid, time+PERIOD)
	def addRes(self, Struct, history, step, formula):
		self.residues.append((step, substitute_stcons(Struct, history, step, (step, formula))))
	def cleanRes(self):
		self.residues = [f for f in self.residues if (f[1] != True and f[1] != False)]
	def cleanHist(self):
		self.history = [i for i in self.history if (i.end >= self.valid-self.delay)]
	def updateHist(self):
		for res in self.residues:
			if (res[1] == True):
				self.addHist(res[0], True)
			elif (res[1] == False):
				self.addHist(res[0], False)
	def incrRes(self, Struct, history, step):
		for i,f in enumerate(self.residues):
			self.residues[i] = (f[0], reduce(substitute_stcons(Struct, history, step, f)))
	def alCheck(self, interval):
		trInt = interval.truncate(self.valid)
		# if truncate is empty, then we can't check any of interval yet
		if (trInt.empty()):
			return ALC_ALIVE
		# can check something, lets look
		found_super = False
		for i in self.history:
			if (i.superset(trInt)):
				found_super = True
		# didn't find always from start to current, violation
		if (not found_super):
			return ALC_VIOLATE
		# found entire interval, satisfies
		elif (found_super and trInt == interval):
			return ALC_SATISFY
		# else found but not finished, keep going
		return ALC_ALIVE
	def __str__(self):
		return "Struct: [%d|| DEL: %d FORM: %s VAL: %d :: HIST: %s, RES: %s]" % (self.tag, self.delay, self.formula, self.valid, self.history, self.residues)
class istructure:
	def __init__(self, tag, formula=[], delay=0):
		self.tag = tag
		self.formula = formula
		self.delay = delay
		self.history = []
		self.residues = []
		self.valid = 0

	def addHist(self, time, val):
		if (val):
			added = False
			for i in self.history:
				if i.extendedBy(time):
					i.addEntry(time)
					added = True
			if (not added):
				self.history.append(Interval(time, time+PERIOD))
		# Add to validity whether True or false
		self.valid = max(self.valid, time+PERIOD)
	def addRes(self, Struct, cstate, time, formula):
		self.residues.append((time, substitute_perint_agp(Struct, cstate, (time, formula))))
	def cleanRes(self):
		self.residues = [f for f in self.residues if (f[1] != True and f[1] != False)]
	def cleanHist(self):
		self.history = [i for i in self.history if (i.end >= self.valid-self.delay)]
	def updateHist(self):
		for res in self.residues:
			if (res[1] == True):
				self.addHist(res[0], True)
			elif (res[1] == False):
				self.addHist(res[0], False)
	def incrRes(self, Struct, cstate):
		for i,f in enumerate(self.residues):
			self.residues[i] = (f[0], reduce(substitute_perint_agp(Struct, cstate, f)))
	def alCheck(self, interval):
		trInt = interval.truncate(self.valid)
		# if truncate is empty, then we can't check any of interval yet
		if (trInt.empty()):
			return ALC_ALIVE
		# can check something, lets look
		found_super = False
		for i in self.history:
			if (i.superset(trInt)):
				found_super = True
		# didn't find always from start to current, violation
		if (not found_super):
			return ALC_VIOLATE
		# found entire interval, satisfies
		elif (found_super and trInt == interval):
			return ALC_SATISFY
		# else found but not finished, keep going
		return ALC_ALIVE
	def __str__(self):
		return "Struct: [%d|| DEL: %d FORM: %s VAL: %d :: HIST: %s, RES: %s]" % (self.tag, self.delay, self.formula, self.valid, self.history, self.residues)
	
class structure:
	def __init__(self, tag, formula=[], delay=0):
		self.tag = tag
		self.formula = formula
		self.delay = delay
		self.history = {}
		self.residues = []
		self.valid = 0

	def addHist(self, time, val):
		self.history[time] = val
		self.valid = max(self.valid, time)
	def addRes(self, time, formula):
		self.residues.append((time,formula))
	def cleanRes(self):
		self.residues = [f for f in self.residues if (f[1] != True and f[1] != False)]
	def cleanHist(self):
		oldhist = [i for i in self.history if (i < (self.valid - self.delay))]
		for i in oldhist:
			del self.history[i]
	def updateHist(self):
		for res in self.residues:
			if (res[1] == True):
				self.addHist(res[0], True)
			elif (res[1] == False):
				self.addHist(res[0], False)
	def incrRes(self, Struct, cstate):
		for i,f in enumerate(self.residues):
			self.residues[i] = (f[0], reduce(substitute_per_agp(Struct, cstate, f)))
	def __str__(self):
		return "Struct: [%d|| DEL: %d FORM: %s VAL: %d :: HIST: %s, RES: %s]" % (self.tag, self.delay, self.formula, self.valid, self.history, self.residues)

class resStructure:
	def __init__(self, formula=[], delay=0):
		self.formula = formula
		self.ctime = 0
		self.delay = delay
		self.residues = []
	# don't need addHist
	def addRes(self, time, formula):
		self.residues.append((time, formula))
		self.ctime = max(self.ctime, time)
	def cleanRes(self, taulist):
		self.residues = [f for f in self.residues if (taulist[f[0]] >= (taulist[self.ctime] - self.delay))]
	def incrRes(self, Struct, cstate, taulist):
		for i,f in enumerate(self.residues):
			self.residues[i] = ag_reduce(Struct, cstate, taulist, f)
	def __str__(self):
		return "resStruct: [DEL: %d FORM: %s CTIME: %d :: RES: %s]" % (self.delay, self.formula, self.ctime, self.residues)

class resIntStructure:
	def __init__(self, formula=[], delay=0):
		self.formula = formula
		self.ctime = 0
		self.delay = delay
		self.residues = []
		self.tint = []
		self.fint = []
	# don't need addHist
	def addRes(self, time, formula):
		self.residues.append((time, formula))
		self.ctime = max(self.ctime, time)
	def cleanRes(self, taulist):
		self.residues = [f for f in self.residues if (taulist[f[0]] >= (taulist[self.ctime] - self.delay))]
		self.tint = [t for t in self.tint if (taulist[t[1]] >= taulist[self.ctime] - self.delay)]
		self.fint = [f for f in self.fint if (taulist[f[1]] >= taulist[self.ctime] - self.delay)]
	def incrRes(self, Struct, cstate, taulist):
		for i,f in enumerate(self.residues):
			resi = ag_reduce(Struct, cstate, taulist, f)
			if (resi[1] == True):
				self.addTrueTime(resi[0])
				self.residues.remove(f)
			elif (resi[1] == False):
				self.addFalseTime(resi[0])
				self.residues.remove(f)
			else:
				self.residues[i] = resi
	def addTrueTime(self, time):
		added = False
		merge = None
		for i,t in enumerate(self.tint):
			if (time-1 == t[1]):
				self.tint[i] = (t[0], time)
				added = True
			elif (time+1 == t[0]):
				if (added):
					# merge!
					merge = i
				else:
					self.tint[i] = (time, t[1]) 
					added = True
		if (merge is not None):
			# need to merge i-1 and i
			newInt = (self.tint[merge-1][0], self.tint[merge][1])
			self.tint[merge-1] = newInt
			del self.tint[merge]
		elif (not added):
			self.tint.append((time,time))
			self.tint.sort()		# stay sorted
	def addFalseTime(self, time):
		added = False
		merge = None
		for i,t in enumerate(self.fint):
			if (time-1 == t[1]):
				self.fint[i] = (t[0], time)
				added = True
			elif (time+1 == t[0]):
				if (added):
					# merge!
					merge = i
				else:
					self.fint[i] = (time, t[1]) 
					added = True
		if (merge is not None):
			# need to merge i-1 and i
			newInt = (self.fint[merge-1][0], self.fint[merge][1])
			self.fint[merge-1] = newInt
			del self.fint[merge]
		elif (not added):
			self.fint.append((time,time))
			self.fint.sort()		# stay sorted
	def __str__(self):
		return "resStruct: [DEL: %d FORM: %s CTIME: %d :: RES: %s || T: %s || F: %s]" % (self.delay, self.formula, self.ctime, self.residues, self.tint, self.fint)

class aStructure:
	def __init__(self, tag, formula=[], delay=0):
		self.tag = tag
		self.formula = formula
		self.delay = delay
		self.history = {}
		self.residues = []
		self.valid = 0

	def addHist(self, time, val):
		self.history[time] = val
		self.valid = max(self.valid, time)
	def addRes(self, time, formula):
		self.residues.append((time,formula))
	def cleanRes(self):
		self.residues = [f for f in self.residues if (f[1] != True and f[1] != False)]
	def cleanHist(self):
		oldhist = [i for i in self.history if (i < (self.valid - self.delay))]
		for i in oldhist:
			del self.history[i]
	def updateHist(self):
		for res in self.residues:
			if (res[1] == True):
				self.addHist(res[0], True)
			elif (res[1] == False):
				self.addHist(res[0], False)
	def incrRes(self, Struct, cstate):
		for i,f in enumerate(self.residues):
			self.residues[i] = (f[0], reduce(substitute_as(Struct, cstate, f)))
	def __str__(self):
		return "aStruct: [%d|| DEL: %d FORM: %s VAL: %d :: HIST: %s, RES: %s]" % (self.tag, self.delay, self.formula, self.valid, self.history, self.residues)

class iStructure:
	def __init__(self, tag, formula=[], delay=0):
		self.tag = tag
		self.formula = formula
		self.delay = delay
		self.history = []
		self.residues = []
		self.valid = 0

	def addHist(self, time, val):
		self.valid = max(self.valid, time)
		if (val):
			added = False
			for i in reversed(self.history):
				if (i.extendedBy(time)):
					i.addEntry(time)
					added = True
					break
			if (not added):
				self.history.append(CInterval(time, time))
	def addRes(self, time, formula):
		self.residues.append((time,formula))
	def cleanRes(self):
		self.residues = [f for f in self.residues if (f[1] != True and f[1] != False)]
	def cleanHist(self):
		self.history = [i for i in self.history if (i.end >= (self.valid - self.delay))]
	def updateHist(self):
		for res in self.residues:
			if (res[1] == True):
				self.addHist(res[0], True)
			elif (res[1] == False):
				self.addHist(res[0], False)
	def incrRes(self, Struct, cstate):
		for i,f in enumerate(self.residues):
			#self.residues[i] = (f[0], reduce(substitute_ais(Struct, cstate, f)))
			self.residues[i] = (f[0], sc_reduce_sub(Struct, cstate, f))
	def alCheck(self, interval):
		trInt = interval.truncate(self.valid)
		# if truncate is empty, then we can't check any of interval yet
		if (trInt.empty()):
			return ALC_ALIVE
		# can check something, lets look
		found_super = False
		for i in reversed(self.history):
			if (i.superset(trInt)):
				found_super = True
		# didn't find always from start to current, violation
		if (not found_super):
			return ALC_VIOLATE
		# found entire interval, satisfies
		elif (found_super and trInt == interval):
			return ALC_SATISFY
		# else found but not finished, keep going
		return ALC_ALIVE

	def __str__(self):
		return "iStruct: [%d|| DEL: %d FORM: %s VAL: %d :: HIST: %s, RES: %s]" % (self.tag, self.delay, self.formula, self.valid, self.history, self.residues)

class Interval(object):
	def __init__(self, start, end):
			self.start = start
			self.end = end

	def __str__(self):
		return "[%d,%d)" % (self.start, self.end)
	def __repr__(self):
		return "[%d,%d)" % (self.start, self.end)

	def __contains__(self, point):
		return (point >= self.start and point < self.end)
	def __eq__(self, other):
		return (self.start == other.start and self.end == other.end)
	def __ne__(self, other):
		return (self.start != other.start or self.end != other.end)

	def intersection(self, interval):
		return Interval(max(self.start, interval.start), min(self.end, interval.end))
	def intersects(self, interval):
		return not self.intersection(interval).empty()
	def addEntry(self, entry):
		if (entry == self.end):
			self.end = entry+PERIOD
			return True
		if (entry == self.start-PERIOD):
			self.start = entry
			return True
		else:
			return False
	def extendedBy(self, entry):
		return (entry == self.end or entry == self.start-PERIOD)
	def truncate(self, v):
		return Interval(self.start, min(self.end, v))
	def superset(self, interval):
		return (self.start <= interval.start and self.end >= interval.end)
	def prop_superset(self, interval):
		return (self.start <= interval.start and self.end > interval.end)
	def empty(self):
		return self.start >= self.end

class CInterval(object):
	def __init__(self, start, end):
			self.start = start
			self.end = end

	def __str__(self):
		return "[%d,%d]" % (self.start, self.end)
	def __repr__(self):
		return "[%d,%d]" % (self.start, self.end)

	def __contains__(self, point):
		return (point >= self.start and point <= self.end)
	def __eq__(self, other):
		return (self.start == other.start and self.end == other.end)
	def __ne__(self, other):
		return (self.start != other.start or self.end != other.end)

	def intersection(self, interval):
		return CInterval(max(self.start, interval.start), min(self.end, interval.end))
	def intersects(self, interval):
		return not self.intersection(interval).empty()
	def addEntry(self, entry):
		if (entry == self.end+PERIOD):
			self.end = entry
			return True
		if (entry == self.start-PERIOD):
			self.start = entry
			return True
		else:
			return False
	def extendedBy(self, entry):
		return (entry == self.end+PERIOD or entry == self.start-PERIOD)
	def truncate(self, v):
		return CInterval(self.start, min(self.end, v))
	def superset(self, interval):
		return (self.start <= interval.start and self.end >= interval.end)
	def prop_superset(self, interval):
		return (self.start < interval.start and self.end > interval.end)
	def empty(self):
		return self.start > self.end

class monTimeData:
	def __init__(self):
		self.loop_t = 0
		self.loop_c = 0
		self.stinc_t = 0
		self.stinc_c = 0
		self.reduce_t = 0
		self.reduce_c = 0
		self.maxres_c = 0
		self.mem_c = 0
		self.mem_n = 0

	def __str__(self):
		return "monTimeData: loop: %s / %s; stinc: %s / %s; reduce: %s / %s; maxres: %s; mem: %s / %s" % (self.loop_t, self.loop_c, self.stinc_t, self.stinc_c, self.reduce_t, self.reduce_c, self.maxres_c, self.mem_c, self.mem_n)
	def __repr__(self):
		return "monTimeData struct"
	def addLoopTime(self, secs):
		self.loop_t += secs
		self.loop_c += 1
	def addStIncTime(self, secs):
		self.stinc_t += secs
		self.stinc_c += 1
	def addReduceTime(self, secs):
		self.reduce_t += secs
		self.reduce_c += 1
	def addMemSize(self, size):
		self.mem_c += size
		self.mem_n += 1
	def checkMaxRes(self, numres):
		self.maxres_c = max(self.maxres_c, numres)

# add a tag to past time formula
def tag_formula(formula):
	global sTag
	formula.insert(3, sTag)
	sTag = sTag + 1
	return (sTag - 1)

# get tag of past-time formula
def get_tags(formula):
	if (len(formula) == 5):
		return formula[3]
	elif (len(formula) == 7):
		return (formula[3], formula[4])
	return -1

ftypeDict = {
	"exp" : EXP_T,
	"prop" : PROP_T,
	"nprop" : NPROP_T,
	"notprop" : NOT_T,
	"andprop" : AND_T,
	"orprop" : OR_T,
	"impprop" : IMPLIES_T,
	"eventprop" : EVENT_T,
	"alwaysprop" : ALWAYS_T,
	"untilprop" : UNTIL_T,
	"onceprop" : PEVENT_T,
	"palwaysprop" : PALWAYS_T,
	"sinceprop" : SINCE_T,
}

def ftype(formula):
	if (formula == 0 or formula == 1 or formula == True or formula == False):
		return VALUE_T
	try:
		return ftypeDict[formula[0]]
	except KeyError:
		return INVALID_T

def ftype_old(formula):
	# check for value (needed for post substitute residual formulas)
	if (formula == 0 or formula == 1 or formula == True or formula == False):
		return VALUE_T
	# then check normal values
	cNode = formula[0]
	if (cNode == "exp"):
		return EXP_T
	elif (cNode == "prop"):
		return PROP_T
	elif (cNode == "nprop"):
		return NPROP_T
	elif (cNode == "notprop"):
		return NOT_T
	elif (cNode == "andprop"):
		return AND_T
	elif (cNode == "orprop"):
		return OR_T
	elif (cNode == "impprop"):
		return IMPLIES_T
	elif (cNode == "eventprop"):
		return EVENT_T
	elif (cNode == "alwaysprop"):
		return ALWAYS_T
	elif (cNode == "untilprop"):
		return UNTIL_T
	#elif (cNode == "peventprop"):
	elif (cNode == "onceprop"):
		return PEVENT_T
	elif (cNode == "palwaysprop"):
		return PALWAYS_T
	elif (cNode == "sinceprop"):
		return SINCE_T
	else:
		return INVALID_T

def not_future(formula):
	if (ftype(formula) == EXP_T):
		return not_future(rchild(formula))
	elif (ftype(formula) == VALUE_T):
		return True
	elif (ftype(formula) == PROP_T):
		return True
	elif (ftype(formula) == NPROP_T):
		return True
	elif (ftype(formula) == NOT_T):
		return not_future(rchild(formula))
	elif (ftype(formula) == AND_T):
		return not_future(lchild(formula)) and not_future(rchild(formula))
	elif (ftype(formula) == OR_T):
		return not_future(lchild(formula)) and not_future(rchild(formula))
	elif (ftype(formula) == IMPLIES_T):
		return not_future(lchild(formula)) and not_future(rchild(formula))
	elif (ftype(formula) == EVENT_T): 
		return False
	elif (ftype(formula) == ALWAYS_T):	
		return False
	elif (ftype(formula) == UNTIL_T): 
		return False
	elif (ftype(formula) == PALWAYS_T):
		return not_future(rchild(formula))
	elif (ftype(formula) == PEVENT_T):
		return not_future(rchild(formula))
	elif (ftype(formula) == SINCE_T):
		return not_future(untilP1(formula)) and not_future(untilP2(formula))
	else:
		# shouldn't get here
		dprint("future checking error...", DBG_ERROR)
		return False

def substitute_as(Struct, cstate, formula_entry):
	ctime = cstate["time"]
	formtime = formula_entry[0]
	formula = formula_entry[1]
	formtype = ftype(formula)
	if (formtype == EXP_T):
		return [formula[0], substitute_as(Struct, cstate, (formtime, formula[1]))]
	elif (formtype == VALUE_T):
		return formula
	elif (formtype == PROP_T):
		if (cstate[formula[1]]):
			return True
		else:
			return False
	elif (formtype == NPROP_T):
		if (cstate[formula[1]]):
			return False
		else:
			return True
	elif (formtype == NOT_T):
		return ['notprop', substitute_as(Struct, cstate, (formtime, formula[1]))]
	elif (formtype == AND_T):
		return ['andprop', substitute_as(Struct, cstate, (formtime, formula[1])), substitute_as(Struct, cstate, (formtime,formula[2]))]
	elif (formtype == OR_T):
		return ['orprop', substitute_as(Struct, cstate, (formtime,formula[1])), substitute_as(Struct, cstate, (formtime, formula[2]))]
	elif (formtype == IMPLIES_T):
		return ['impprop', substitute_as(Struct, cstate, (formtime,formula[1])), substitute_as(Struct, cstate, (formtime, formula[2]))]
	elif (formtype == EVENT_T): 
		h = hbound(formula) + formtime
		l = lbound(formula) + formtime
		subStruct = Struct[get_tags(formula)]
		sthist = subStruct.history
		#
		for i in sthist:
			if (i > h):
				break
			elif (l <= i):
				if sthist[i]:
					return True
		if subStruct.valid >= h:
			return False
		return formula
	elif (formtype == ALWAYS_T):
		h = hbound(formula) + formtime
		l = lbound(formula) + formtime
		subStruct = Struct[get_tags(formula)]
		sthist = subStruct.history
		#
		for i in sthist:
			if (i > h):
				break
			elif (l <= i):
				if not sthist[i]:
					return False
		if subStruct.valid >= h:
			return True
		return formula
	elif (formtype == UNTIL_T): 
		tags = get_tags(formula)
		subStruct1 = Struct[tags[0]]
		subStruct2 = Struct[tags[1]]
		sthist1 = subStruct1.history
		sthist2 = subStruct2.history
		h = hbound(formula) + formtime
		l = lbound(formula) + formtime
		end = None
		#done = True

		for i in sthist2:
			if (i > h):
				break
			elif (l <= i):
				end = i
				# don't break, want the latest i
		#
		if (end is None and subStruct2.valid >= h):
			return False
		elif (end is None):
			#done = False
			end = ctime

		l = formtime	
		h = end
		for i in sthist1:
			if (i > h):
				break
			#elif (l <= i):
			# usual semantics is l < i, so using that
			elif (l < i):
				if not sthist1[i]:
					return False
		# always is surviving, did we find eventually? done if so
		#if done and subStruct1.valid >= h:
		if subStruct1.valid >= h:
			return True
		# still haven't seen eventually, hang on
		return formula
	elif (formtype == PEVENT_T):
		h = formtime - lbound(formula)
		l = formtime - hbound(formula)
		subStruct = Struct[get_tags(formula)]
		sthist = subStruct.history
		#
		for i in sthist:
			if (i > h):
				break
			elif (l <= i):
				if sthist[i]:
					return True
		if subStruct.valid >= h:
			return False
		return formula
	elif (formtype == PALWAYS_T):
		h = formtime - lbound(formula)
		l = formtime - hbound(formula)
		subStruct = Struct[get_tags(formula)]
		sthist = subStruct.history
		#
		for i in sthist:
			if (i > h):
				break
			elif (l <= i):
				if not sthist[i]:
					return False
		if subStruct.valid >= h:
			return True
		return formula
	elif (formtype == SINCE_T):
		tags = get_tags(formula)
		subStruct1 = Struct[tags[0]]
		subStruct2 = Struct[tags[1]]
		sthist1 = subStruct1.history
		sthist2 = subStruct2.history
		h = formtime - lbound(formula)
		l = formtime - hbound(formula)
		start = None
		#
		for i in sthist2:
			if (i > h):
				break
			elif (l <= i):
				if sthist2[i]:
					start = i
					# don't break because we want the most recent P1
					#break
		#
		if (start is None and subStruct2.valid >= h):
			return False
		elif (start is None):
			# haven't seen eventually yet, can't check always
			return formula

		l = start 
		h = formtime
		for i in sthist1:
			if (i > h):
				break
			#elif (l <= i):
			# using l < i since that's the usual semantics
			elif (l < i):
				if not sthist1[i]:
					return False
		# always is surviving, can we see all of it?
		if subStruct1.valid >= h:
			return True
		# still waiting on P1 to be valid up to current formula time
		return formula
	else:
		return INVALID_T

def substitute_ais(Struct, cstate, formula_entry):
	ctime = cstate["time"]
	formtime = formula_entry[0]
	formula = formula_entry[1]
	formtype = ftype(formula)
	if (formtype == EXP_T):
		return [formula[0], substitute_ais(Struct, cstate, (formtime, formula[1]))]
	elif (formtype == VALUE_T):
		return formula
	elif (formtype == PROP_T):
		if (cstate[formula[1]]):
			return True
		else:
			return False
	elif (formtype == NPROP_T):
		if (cstate[formula[1]]):
			return False
		else:
			return True
	elif (formtype == NOT_T):
		return ['notprop', substitute_ais(Struct, cstate, (formtime, formula[1]))]
	elif (formtype == AND_T):
		return ['andprop', substitute_ais(Struct, cstate, (formtime, formula[1])), substitute_ais(Struct, cstate, (formtime,formula[2]))]
	elif (formtype == OR_T):
		return ['orprop', substitute_ais(Struct, cstate, (formtime,formula[1])), substitute_ais(Struct, cstate, (formtime, formula[2]))]
	elif (formtype == IMPLIES_T):
		return ['impprop', substitute_ais(Struct, cstate, (formtime,formula[1])), substitute_ais(Struct, cstate, (formtime, formula[2]))]
	elif (formtype == EVENT_T): 
		h = hbound(formula) + formtime
		l = lbound(formula) + formtime
		subStruct = Struct[get_tags(formula)]
		sthist = subStruct.history
		check = CInterval(l,h)
		#
		for i in sthist:
			if i.intersects(check):
				return True
		if (subStruct.valid >= h):
			return False
		return formula
	elif (formtype == ALWAYS_T):
		h = hbound(formula) + formtime
		l = lbound(formula) + formtime
		subStruct = Struct[get_tags(formula)]
		sthist = subStruct.history
		check = CInterval(l,h)
		#
		alcheck = subStruct.alCheck(check)
		if (alcheck == ALC_SATISFY):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE
			return formula
	elif (formtype == UNTIL_T): 
		tags = get_tags(formula)
		subStruct1 = Struct[tags[0]]
		subStruct2 = Struct[tags[1]]
		sthist1 = subStruct1.history
		sthist2 = subStruct2.history
		h = hbound(formula) + formtime
		l = lbound(formula) + formtime
		check = CInterval(l,h)
		end = None
		#done = True

		for i in sthist2:
			if i.intersects(check):
				end = i.intersection(check).end
		# didn't find P2 and past time
		if (end is None and subStruct2.valid >= h):
			return False
		elif (end is None):
			end = ctime

		l = formtime	
		h = end
		check = CInterval(l,h)
		alcheck = subStruct1.alCheck(check)

		if (alcheck == ALC_SATISFY and subStruct2.valid >= h):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE or ALC_SAT and not found
			return formula
	elif (formtype == PEVENT_T):
		h = formtime - lbound(formula)
		l = formtime - hbound(formula)
		subStruct = Struct[get_tags(formula)]
		sthist = subStruct.history
		check = CInterval(l,h)
		#
		for i in sthist:
			if i.intersects(check):
				return True
		if subStruct.valid >= h:
			return False
		return formula
	elif (formtype == PALWAYS_T):
		h = formtime - lbound(formula)
		l = formtime - hbound(formula)
		subStruct = Struct[get_tags(formula)]
		sthist = subStruct.history
		check = CInterval(l,h)
		#
		alcheck = subStruct.alCheck(check)
		if (alcheck == ALC_SATISFY):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE
			return formula
	elif (formtype == SINCE_T):
		tags = get_tags(formula)
		subStruct1 = Struct[tags[0]]
		subStruct2 = Struct[tags[1]]
		sthist1 = subStruct1.history
		sthist2 = subStruct2.history
		h = formtime - lbound(formula)
		l = formtime - hbound(formula)
		start = None
		check = CInterval(l,h)
		#
		#print "checking since at %s" % check
		#print "eventhist: %s" % sthist2
		for i in sthist2:
			if i.intersects(check):
				start = i.intersection(check).end
		if (start is None and subStruct2.valid >= h):
			return False
		elif (start is None):
			# haven't seen eventually yet, can't check always
			return formula

		l = start + PERIOD
		h = formtime
		check = CInterval(l,h)
		alcheck = subStruct1.alCheck(check)

		#print "checking always at %s" % check
		#print "alwayshist: %s" % sthist1
		if (alcheck == ALC_SATISFY or alcheck == ALC_ALIVE and subStruct2.valid >= h):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE or ALC_SAT and not found
			return formula
	else:
		return INVALID_T

def substitute_per_agp(Struct, cstate, formula_entry):
	ctime = cstate["time"]
	formtime = formula_entry[0]
	formula = formula_entry[1]
	if (ftype(formula) == EXP_T):
		return [formula[0], substitute_per_agp(Struct, cstate, (formtime, formula[1]))]
	elif (ftype(formula) == VALUE_T):
		return formula
	elif (ftype(formula) == PROP_T):
		#return cstate[formula[1]]
		if (cstate[formula[1]]):
			return True
		else:
			return False
	elif (ftype(formula) == NPROP_T):
		#return not cstate[formula[1]]
		if (cstate[formula[1]]):
			return False
		else:
			return True
	elif (ftype(formula) == NOT_T):
		return ['notprop', substitute_per_agp(Struct, cstate, (formtime, formula[1]))]
	elif (ftype(formula) == AND_T):
		return ['andprop', substitute_per_agp(Struct, cstate, (formtime, formula[1])), substitute_per_agp(Struct, cstate, (formtime,formula[2]))]
	elif (ftype(formula) == OR_T):
		return ['orprop', substitute_per_agp(Struct, cstate, (formtime,formula[1])), substitute_per_agp(Struct, cstate, (formtime, formula[2]))]
	elif (ftype(formula) == IMPLIES_T):
		return ['impprop', substitute_per_agp(Struct, cstate, (formtime,formula[1])), substitute_per_agp(Struct, cstate, (formtime, formula[2]))]
	elif (ftype(formula) == EVENT_T): 
		subStruct = Struct[get_tags(formula)]
		sEnd = hbound(formula) + formtime
		sStart = lbound(formula) + formtime
		allF = True
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct.history):
				if (subStruct.history[t] == True):
					return True
			else:
				allF = False
		# if we're past the time we have to have an answer, we didn't see the eventually
		if (allF == True):# or ctime > formtime + wdelay(formula)):
			return False
		return formula
	elif (ftype(formula) == ALWAYS_T):
		subStruct = Struct[get_tags(formula)]
		sEnd = hbound(formula) + formtime
		sStart = lbound(formula) + formtime
		allT = True
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct.history):
				if (subStruct.history[t] == False):
					return False
			else:
				allT = False
		# past time and still alive, return true
		if (allT == True):
			return True
		# trying explicit checking for True return first
		#if (ctime > formtime + wdelay(formula)):
		#	return True
		return formula
	elif (ftype(formula) == UNTIL_T): 
		tags = get_tags(formula)
		subStruct1 = Struct[tags[0]]
		subStruct2 = Struct[tags[1]]
		sEnd = hbound(formula) + formtime
		sStart = lbound(formula) + formtime
		end = None
		allF = True
		maxvalid = -1
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct2.history):
				maxvalid = max(maxvalid, t)
				if (subStruct2.history[t] == True):
					end = t
					allF = False
					break
			else:
				allF = False
		# if we're past the time we have to have an answer, we didn't see the eventually
		# TODO need aggressive until/since, gotta check current but be able to wait for P2
		found = True
		if allF:
			return False
		elif (end is None):
			end = maxvalid
			found = False
		
		# did find eventually, check P1
		sEnd = end
		sStart = formtime
		allT = True
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct1.history):
				if (subStruct1.history[t] == False):
					return False
			else:
				allT = False
		# past time and still alive, return true
		if (allT == True and found):
			return True
		return formula
	elif (ftype(formula) == PEVENT_T):
		subStruct = Struct[get_tags(formula)]
		sEnd = formtime - lbound(formula)
		sStart = formtime - hbound(formula)
		allF = True
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct.history):
				if (subStruct.history[t] == True):
					return True
			else:
				allF = False
		# if we're past the time we have to have an answer, we didn't see the eventually
		if (allF == True):	# or ctime > formtime + wdelay(formula)):
			return False
		return formula
	elif (ftype(formula) == PALWAYS_T):
		subStruct = Struct[get_tags(formula)]
		sEnd = formtime - lbound(formula)
		sStart = formtime - hbound(formula)
		allT = True
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct.history):
				if (subStruct.history[t] == False):
					return False
			else:
				allT = False
		# past time and still alive, return true
		if (allT == True):
			return True
		# trying explicit checking for True return first
		#if (ctime > formtime + wdelay(formula)):
		#	return True
		return formula
	elif (ftype(formula) == SINCE_T):
		tags = get_tags(formula)
		subStruct1 = Struct[tags[0]]
		subStruct2 = Struct[tags[1]]
		sEnd = formtime - lbound(formula)
		sStart = formtime - hbound(formula)
		start = None
		allF = True
		#print "checking (%d,%d)" % (sStart, sEnd)
		#print "sub: %s" % subStruct2
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct2.history):
				if (subStruct2.history[t] == True):
					start = t
					allF = False
					break
			else:
				allF = False
		# if we're past the time we have to have an answer, we didn't see the eventually
		#print "start: %s" % start
		found = True
		if allF: 
			return False
		elif (start is None):
			return formula

		# did find eventually, check P1
		sEnd = formtime
		sStart = start
		allT = True
		#print "checking (%d,%d)" % (sStart, sEnd)
		#print "sub: %s" % subStruct1
		for t in range(sStart, sEnd+PERIOD, PERIOD):
			if (t in subStruct1.history):
				if (subStruct1.history[t] == False):
					return False
			else:
				allT = False
		# past time and still alive, return true
		if (allT == True):
			return True
		return formula
	else:
		return INVALID_T

def substitute_perint_agp(Struct, cstate, formula_entry):
	ctime = cstate["time"]
	formtime = formula_entry[0]
	formula = formula_entry[1]
	if (ftype(formula) == EXP_T):
		return [formula[0], substitute_perint_agp(Struct, cstate, (formtime, formula[1]))]
	elif (ftype(formula) == VALUE_T):
		return formula
	elif (ftype(formula) == PROP_T):
		#return cstate[formula[1]]
		if (cstate[formula[1]]):
			return True
		else:
			return False
	elif (ftype(formula) == NPROP_T):
		#return not cstate[formula[1]]
		if (cstate[formula[1]]):
			return False
		else:
			return True
	elif (ftype(formula) == NOT_T):
		return ['notprop', substitute_perint_agp(Struct, cstate, (formtime, formula[1]))]
	elif (ftype(formula) == AND_T):
		return ['andprop', substitute_perint_agp(Struct, cstate, (formtime, formula[1])), substitute_perint_agp(Struct, cstate, (formtime,formula[2]))]
	elif (ftype(formula) == OR_T):
		return ['orprop', substitute_perint_agp(Struct, cstate, (formtime,formula[1])), substitute_perint_agp(Struct, cstate, (formtime, formula[2]))]
	elif (ftype(formula) == IMPLIES_T):
		return ['impprop', substitute_perint_agp(Struct, cstate, (formtime,formula[1])), substitute_perint_agp(Struct, cstate, (formtime, formula[2]))]
	elif (ftype(formula) == EVENT_T): 
		subStruct = Struct[get_tags(formula)]
		sEnd = hbound(formula) + formtime
		sStart = lbound(formula) + formtime
		check = Interval(sStart, sEnd+PERIOD)
		
		for i in subStruct.history:
			if i.intersects(check):
				return True
		# not waiting on any data, if formula satisfied would've returned true above
		if (subStruct.valid > sEnd):
			return False
		return formula
	elif (ftype(formula) == ALWAYS_T):
		subStruct = Struct[get_tags(formula)]
		sEnd = hbound(formula) + formtime
		sStart = lbound(formula) + formtime
		check = Interval(sStart, sEnd+PERIOD)

		alcheck = subStruct.alCheck(check)
		if (alcheck == ALC_SATISFY):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE
			return formula
	elif (ftype(formula) == UNTIL_T): 
		tags = get_tags(formula)
		subStruct1 = Struct[tags[0]]
		subStruct2 = Struct[tags[1]]
		sEnd = hbound(formula) + formtime
		sStart = lbound(formula) + formtime
		check = Interval(sStart, sEnd+PERIOD)
		end = None
		efound = True

		for i in subStruct2.history:
			if i.intersects(check):
				end = i.intersection(check).start
		# didn't find P2 and past time
		if (end is None and subStruct2.valid > sEnd):
			return False
		elif (end is None):
			end = subStruct2.valid
			efound = False
		
		# did find eventually, check P1
		sEnd = end + PERIOD		# end value is inclusive
		sStart = formtime
		check = Interval(sStart, sEnd)
		alcheck = subStruct1.alCheck(check)

		if (alcheck == ALC_SATISFY and efound):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE or ALC_SAT and not found
			return formula
	elif (ftype(formula) == PEVENT_T):
		subStruct = Struct[get_tags(formula)]
		sEnd = formtime - lbound(formula)
		sStart = formtime - hbound(formula)
		check = Interval(sStart, sEnd+PERIOD)
		
		for i in subStruct.history:
			if i.intersects(check):
				return True
		# not waiting on any data, if formula satisfied would've returned true above
		if (subStruct.valid > sEnd):
			return False
		return formula
	elif (ftype(formula) == PALWAYS_T):
		subStruct = Struct[get_tags(formula)]
		sEnd = formtime - lbound(formula)
		sStart = formtime - hbound(formula)
		check = Interval(sStart, sEnd+PERIOD)

		alcheck = subStruct.alCheck(check)
		if (alcheck == ALC_SATISFY):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE
			return formula
	elif (ftype(formula) == SINCE_T):
		tags = get_tags(formula)
		subStruct1 = Struct[tags[0]]
		subStruct2 = Struct[tags[1]]
		sEnd = formtime - lbound(formula)
		sStart = formtime - hbound(formula)


		check = Interval(sStart, sEnd+PERIOD)
		start = None
		efound = True

		for i in subStruct2.history:
			if i.intersects(check):
				start = i.intersection(check).start
		# didn't find P2 and past time
		if (start is None and subStruct2.valid > sEnd):
			return False
		elif (start is None):
			start = subStruct2.valid
			efound = False

		# did find eventually, check P1
		sEnd = formtime + PERIOD	# end is inclusive
		sStart = start 
		check = Interval(sStart, sEnd)
		alcheck = subStruct1.alCheck(check)

		if (alcheck == ALC_SATISFY and efound):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE or ALC_SAT and not found
			return formula
	else:
		return INVALID_T

def substitute_stcons(Struct, history, eptr, formula_entry):
	formtime = formula_entry[0]
	formula = formula_entry[1]
	if (ftype(formula) == EXP_T):
		return [formula[0], substitute_stcons(Struct, history, eptr, (formtime, lchild(formula)))]
	elif (ftype(formula) == VALUE_T):
		return formula
	elif (ftype(formula) == PROP_T):
		if (history[eptr][lchild(formula)]):
			return True
		else:
			return False
	elif (ftype(formula) == NPROP_T):
		if (history[eptr][lchild(formula)]):
			return False
		else:
			return True
	elif (ftype(formula) == NOT_T):
		return ['notprop', substitute_stcons(Struct, history, eptr, (formtime, lchild(formula)))]
	elif (ftype(formula) == AND_T):
		return ['andprop', substitute_stcons(Struct, history, eptr, (formtime, lchild(formula))), substitute_stcons(Struct, history, eptr, (formtime,rchild(formula)))]
	elif (ftype(formula) == OR_T):
		return ['orprop', substitute_stcons(Struct, history, eptr, (formtime,lchild(formula))), substitute_stcons(Struct, history, eptr, (formtime, rchild(formula)))]
	elif (ftype(formula) == IMPLIES_T):
		return ['impprop', substitute_stcons(Struct, history, eptr, (formtime,lchild(formula))), substitute_stcons(Struct, history, eptr, (formtime, rchild(formula)))]
	elif (ftype(formula) == EVENT_T): 
		l = lbound(formula) + formtime
		h = hbound(formula) + formtime
		
		for i in range(l, h+PERIOD):
			if reduce(substitute_stcons(Struct, history, i, (i, rchild(formula)))):
				return True
		return False
	elif (ftype(formula) == ALWAYS_T):
		l = lbound(formula) + formtime
		h = hbound(formula) + formtime

		for i in range(l, h+PERIOD):
			if (not reduce(substitute_stcons(Struct, history, i, (i, rchild(formula))))):
				return False
		return True
	elif (ftype(formula) == UNTIL_T): 
		l = lbound(formula) + formtime
		h = hbound(formula) + formtime
		end = None
		for i in range(l, h+PERIOD):
			if reduce(substitute_stcons(Struct, history, i, (i, untilP2(formula)))):
				end = i
				break
		if (end is None):
			return False
		#
		l = formtime
		h = end

		for i in range(l, h+PERIOD):
			if (not reduce(substitute_stcons(Struct, history, i, (i, untilP1(formula))))):
				return False
		return True
	elif (ftype(formula) == PEVENT_T):
		if (not_future(formula)):
			subStruct = Struct[get_tags(formula)]
			sEnd = formtime - lbound(formula)
			sStart = formtime - hbound(formula)
			check = Interval(sStart, sEnd+PERIOD)
			
			for i in subStruct.history:
				if i.intersects(check):
					return True
			# not waiting on any data, if formula satisfied would've returned true above
			if (subStruct.valid > sEnd):
				return False
			return formula
		#### Nested, Don't have struct, check manually
		else:
			l = formtime - hbound(formula)
			h = formtime - lbound(formula)
			
			for i in range(l, h+PERIOD):
				if reduce(substitute_stcons(Struct, history, i, (i, rchild(formula)))):
					return True
			return False
	elif (ftype(formula) == PALWAYS_T):
		if (not_future(formula)):
			subStruct = Struct[get_tags(formula)]
			sEnd = formtime - lbound(formula)
			sStart = formtime - hbound(formula)
			check = Interval(sStart, sEnd+PERIOD)

			alcheck = subStruct.alCheck(check)
			if (alcheck == ALC_SATISFY):
				return True
			elif (alcheck == ALC_VIOLATE):
				return False
			else: # alcheck == ALC_ALIVE
				return formula
		#### nested future, don't have struct, check manually
		else: 
			l = formtime - hbound(formula)
			h = formtime - lbound(formula)

			for i in range(l, h+PERIOD):
				if (not reduce(substitute_stcons(Struct, history, i, (i, rchild(formula))))):
					return False
			return True
	elif (ftype(formula) == SINCE_T):
		if (not_future(formula)):
			tags = get_tags(formula)
			subStruct1 = Struct[tags[0]]
			subStruct2 = Struct[tags[1]]
			sEnd = formtime - lbound(formula)
			sStart = formtime - hbound(formula)

			check = Interval(sStart, sEnd+PERIOD)
			start = None
			efound = True

			for i in subStruct2.history:
				if i.intersects(check):
					start = i.intersection(check).start
			# didn't find P2 and past time
			if (start is None and subStruct2.valid > sEnd):
				return False
			elif (start is None):
				start = subStruct2.valid
				efound = False

			# did find eventually, check P1
			sEnd = formtime + PERIOD	# end is inclusive
			sStart = start 
			check = Interval(sStart, sEnd)
			alcheck = subStruct1.alCheck(check)

			if (alcheck == ALC_SATISFY and efound):
				return True
			elif (alcheck == ALC_VIOLATE):
				return False
			else: # alcheck == ALC_ALIVE or ALC_SAT and not found
				return formula
		# nested future, don't have struct, check manually
		else:
			l = formtime - hbound(formula)
			h = formtime - lbound(formula)
			start = None
			for i in range(l, h+PERIOD):
				if reduce(substitute_stcons(Struct, history, i, (i, untilP2(formula)))):
					end = i
					break
			if (start is None):
				return False
			#
			l = start
			h = formtime 
			for i in range(l, h+PERIOD):
				if (not reduce(substitute_stcons(Struct, history, i, (i, untilP1(formula))))):
					return False
			return True
	else:
		return INVALID_T

def simplify(formula):
	if (ftype(formula) == EXP_T):
		#return [formula[0], simplify(formula[1])]
		return simplify(formula[1])
	elif (ftype(formula) == VALUE_T):
		return formula
	elif (ftype(formula) == PROP_T):
		dprint("shouldn't get here, already sub'd", DBG_ERROR)
		return cstate[formula[1]]
	elif (ftype(formula) == NPROP_T):
		dprint("shouldn't get here, already sub'd", DBG_ERROR)
		return not cstate[formula[1]]
	elif (ftype(formula) == NOT_T):
		child = simplify(formula[1])
		if (ftype(child) == VALUE_T):
			return not child
		else:
			return ['notprop', child]
	elif (ftype(formula) == AND_T):
		child1 = simplify(formula[1])
		child2 = simplify(formula[2])
		if (child1 == False or child2 == False):
			return False
		elif (child1 == True and child2 == True):
			return True
		else:
			return ['andprop', child1, child2]
	elif (ftype(formula) == OR_T):
		child1 = simplify(formula[1])
		child2 = simplify(formula[2])
		if (child1 == True or child2 == True):
			return True
		elif (child1 == False and child2 == False):
			return False
		else:
			return ['orprop', child1, child2]
	elif (ftype(formula) == IMPLIES_T):
		child1 = simplify(formula[1])
		child2 = simplify(formula[2])
		if (child1 == False or child2 == True):
			return True
		elif (child1 == True and child2 == False):
			return False
		else:
			return ['impprop', child1, child2]
	elif (ftype(formula) == EVENT_T): 
		## Fill in with check and return formula if not sure yet
		return formula
	elif (ftype(formula) == ALWAYS_T):
		## Fill in with check and return formula if not sure yet
		return formula
	elif (ftype(formula) == UNTIL_T): 
		## Fill in with check and return formula if not sure yet
		return formula
	elif (ftype(formula) == PEVENT_T):
		return formula
	elif (ftype(formula) == PALWAYS_T):
		return formula
	elif (ftype(formula) == SINCE_T):
		return formula
	else:
		return INVALID_T

def ag_reduce(Struct, cstate, taulist, formula_entry):
	ctime = cstate["time"]
	formtime = formula_entry[0]
	formula = formula_entry[1]
	formtype = ftype(formula)
	if (formtype == VALUE_T):
		return (formtime, formula)
	elif (formtype == PROP_T):
		if (cstate[formula[1]]):
			return (formtime, True)
		else:
			return (formtime, False)
	elif (formtype == NOT_T):
		child = ag_reduce(Struct, cstate, taulist, (formtime, formula[1]))
		child = simplify(['notprop', child[1]])
		return (formtime, child)
	elif (formtype == OR_T):
		child1 = ag_reduce(Struct, cstate, taulist, (formtime, formula[1]))
		child2 = ag_reduce(Struct, cstate, taulist, (formtime, formula[2]))
		ans = simplify(['orprop', child1[1], child2[1]])
		return (formtime, ans)
	elif (formtype == UNTIL_T): 
		tags = get_tags(formula)
		st_alpha = Struct[tags[0]].residues
		st_beta = Struct[tags[1]].residues
		st_betatime = Struct[tags[1]].ctime
		#hst_alpha = st_alpha.history
		#hst_beta = st_beta.history
		h = hbound(formula) + taulist[formtime]
		l = lbound(formula) + taulist[formtime]

		# get spot alpha is alive until
		st_alpha_bound = sorted([i for i in st_alpha if rstep(i) in taulist and taulist[formtime] <= taulist[rstep(i)] <= h])
		st_beta_bound = sorted([i for i in st_beta if rstep(i) in taulist and l <= taulist[rstep(i)] <= h])

		# find the spot alpha could be true until
		a_alive = None
		for i in st_alpha_bound:
			if (rform(i) == False):
				a_alive = rstep(i)
				break
		# get spot alpha is true until
		a_until = formtime - 1 
		for i in st_alpha_bound:
			if (rform(i) == True):
				a_until = rstep(i)
			else:
				break	# quit once we find a not-true
		# find the lowest possible time for beta
		b_alive = None
		for i in st_beta_bound:
			if (rform(i) != False):
				b_alive = rstep(i)
				break
		# find the lowest actual beta
		b_actual = None
		for i in st_beta_bound:
			if (rform(i) == True):
				b_actual = rstep(i)
				break
		# all beta's false?
		b_none = None
		if (ctime >= h):
			b_none = True
			for i in st_beta_bound:
				if (rform(i) != False):
					b_none = False
					break

		#dprint("beta: %s" % (st_beta,))
		#dprint("checking until at %i" % formtime)
		#dprint("bbound: %s" % (st_beta_bound,))
		#dprint("abound: %s" % (st_alpha_bound,))
		#dprint("until debug: a_al: %s, a_u: %s, b_al: %s, b_ac: %s, b_none: %s" % (a_alive, a_until, b_alive, b_actual, b_none))
		if (b_actual is not None and a_until is not None and b_actual-1 <= a_until):
			return (formtime, True)
		# first a false can be = to first be non-false, but can't be before
		elif (b_alive is not None and a_alive is not None and a_alive < b_alive):
			return (formtime, False)
		elif (b_none == True):
			return (formtime, False)
		else:
			return (formtime, formula)
	elif (formtype == SINCE_T):
		tags = get_tags(formula)
		st_alpha = Struct[tags[0]].residues
		st_beta = Struct[tags[1]].residues
		st_betatime = Struct[tags[1]].ctime
		#hst_alpha = st_alpha.history
		#hst_beta = st_beta.history
		h = taulist[formtime] - lbound(formula)
		l = taulist[formtime] - hbound(formula)

		# get spot alpha is alive until
		st_alpha_bound = sorted([i for i in st_alpha if (rstep(i) in taulist and l <= taulist[rstep(i)] <= formtime)])
		st_beta_bound = sorted([i for i in st_beta if (rstep(i) in taulist and l <= taulist[rstep(i)] <= h)])

		st_alpha_bound.reverse()	
		st_beta_bound.reverse()
		# find the spot alpha could be true since (highest false in range)
		a_alive = None
		for i in st_alpha_bound:
			if (rform(i) == False):
				a_alive = rstep(i)
				break
		# get spot alpha is true since (lowest value in chain of true's)
		#a_since = None
		a_since = formtime + 1
		for i in st_alpha_bound:
			if (rform(i) == True):
				a_since = rstep(i)
			else:
				break	# quit once we find a not-true
		# find the most recent possible time for beta (highest)
		b_alive = None
		for i in st_beta_bound:
			if (rform(i) != False):
				b_alive = rstep(i)
				break
		# find the most recent actual beta (highest)
		b_actual = None
		for i in st_beta_bound:
			if (rform(i) == True):
				b_actual = rstep(i)
				break
		# all beta's false?
		b_none = None
		if (ctime >= h):
			b_none = True
			for i in st_beta_bound:
				if (rform(i) != False):
					b_none = False
					break

		#dprint("bbound: %s" % (st_beta_bound,))
		#dprint("abound: %s" % (st_alpha_bound,))
		#dprint("since debug: a_al: %s, a_s: %s, b_al: %s, b_ac: %s, b_none: %s" % (a_alive, a_since, b_alive, b_actual, b_none))
		if (b_actual is not None and a_since is not None and b_actual+1 >= a_since):# or b_actual == formtime):
			return (formtime, True)
		elif (b_alive is not None and a_alive is not None and a_alive > b_alive):
			return (formtime, False)
		elif (b_none == True):
			return (formtime, False)
		else:
			return (formtime, formula)
	else:
		return INVALID_T

def sc_reduce_sub(Struct, cstate, formula_entry):
	ctime = cstate["time"]
	formtime = formula_entry[0]
	formula = formula_entry[1]
	formtype = ftype(formula)
	if (formtype == EXP_T):
		return sc_reduce_sub(Struct, cstate, (formtime, formula[1]))
	elif (formtype == VALUE_T):
		return formula
	elif (formtype == PROP_T):
		if (cstate[formula[1]]):
			return True
		else:
			return False
	elif (formtype == NPROP_T):
		if (cstate[formula[1]]):
			return False
		else:
			return True
	elif (formtype == NOT_T):
		child = sc_reduce_sub(Struct, cstate, (formtime, formula[1]))
		if (ftype(child) == VALUE_T):
			return not child
		else:
			return ['notprop', child]
	elif (formtype == AND_T):
		child1 = sc_reduce_sub(Struct, cstate, (formtime, formula[1]))
		child2 = formula[2]
		if (child1 == False):
			return False
		elif (child1 == True):
			child2 = sc_reduce_sub(Struct, cstate, (formtime, formula[2]))
			if (ftype(child2) == VALUE_T):
				return child2
		# otherwise child1 undetermined or child2 underdetermined
		return ['andprop', child1, child2]	
	elif (formtype == OR_T):
		child1 = sc_reduce_sub(Struct, cstate, (formtime, formula[1]))
		if (child1 == True):
			return True
		child2 = sc_reduce_sub(Struct, cstate, (formtime, formula[2]))
		if (child2 == True):
			return True
		elif (child1 == False and child2 == False):
			return False
		else:
			return ['orprop', child1, child2]
	elif (formtype == IMPLIES_T):
		child1 = sc_reduce_sub(Struct, cstate, (formtime, formula[1]))
		if (child1 == False):
			return True
		child2 = sc_reduce_sub(Struct, cstate, (formtime, formula[2]))
		if (child2 == True):
			return True
		elif (child1 == True and child2 == False):
			return False
		else:
			return ['impprop', child1, child2]
	elif (formtype == EVENT_T): 
		h = hbound(formula) + formtime
		l = lbound(formula) + formtime
		subStruct = Struct[get_tags(formula)]
		sthist = subStruct.history
		check = CInterval(l,h)
		#
		for i in reversed(sthist):
			if i.intersects(check):
				return True
		if (subStruct.valid >= h):
			return False
		return formula
	elif (formtype == ALWAYS_T):
		h = hbound(formula) + formtime
		l = lbound(formula) + formtime
		subStruct = Struct[get_tags(formula)]
		sthist = subStruct.history
		check = CInterval(l,h)
		#
		alcheck = subStruct.alCheck(check)
		if (alcheck == ALC_SATISFY):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE
			return formula
	elif (formtype == UNTIL_T): 
		tags = get_tags(formula)
		subStruct1 = Struct[tags[0]]
		subStruct2 = Struct[tags[1]]
		sthist1 = subStruct1.history
		sthist2 = subStruct2.history
		h = hbound(formula) + formtime
		l = lbound(formula) + formtime
		check = CInterval(l,h)
		end = None
		#done = True

		for i in reversed(sthist2):
			if i.intersects(check):
				end = i.intersection(check).end
				break	# find the most recent one
		# didn't find P2 and past time
		if (end is None and subStruct2.valid >= h):
			return False
		elif (end is None):
			end = ctime

		l = formtime	
		h = end
		check = CInterval(l,h)
		alcheck = subStruct1.alCheck(check)

		if (alcheck == ALC_SATISFY and subStruct2.valid >= h):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE or ALC_SAT and not found
			return formula
	elif (formtype == PEVENT_T):
		h = formtime - lbound(formula)
		l = formtime - hbound(formula)
		subStruct = Struct[get_tags(formula)]
		sthist = subStruct.history
		check = CInterval(l,h)
		#
		for i in reversed(sthist):
			if i.intersects(check):
				return True
		if subStruct.valid >= h:
			return False
		return formula
	elif (formtype == PALWAYS_T):
		h = formtime - lbound(formula)
		l = formtime - hbound(formula)
		subStruct = Struct[get_tags(formula)]
		sthist = subStruct.history
		check = CInterval(l,h)
		#
		alcheck = subStruct.alCheck(check)
		if (alcheck == ALC_SATISFY):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE
			return formula
	elif (formtype == SINCE_T):
		tags = get_tags(formula)
		subStruct1 = Struct[tags[0]]
		subStruct2 = Struct[tags[1]]
		sthist1 = subStruct1.history
		sthist2 = subStruct2.history
		h = formtime - lbound(formula)
		l = formtime - hbound(formula)
		start = None
		check = CInterval(l,h)
		#
		#print "checking since at %s" % check
		#print "eventhist: %s" % sthist2
		for i in reversed(sthist2):
			if i.intersects(check):
				start = i.intersection(check).end
				break	# find the most recent one
		if (start is None and subStruct2.valid >= h):
			return False
		elif (start is None):
			# haven't seen eventually yet, can't check always
			return formula

		l = start + PERIOD
		h = formtime
		check = CInterval(l,h)
		alcheck = subStruct1.alCheck(check)

		#print "checking always at %s" % check
		#print "alwayshist: %s" % sthist1
		if (alcheck == ALC_SATISFY or alcheck == ALC_ALIVE and subStruct2.valid >= h):
			return True
		elif (alcheck == ALC_VIOLATE):
			return False
		else: # alcheck == ALC_ALIVE or ALC_SAT and not found
			return formula
	else:
		return INVALID_T



def ag_simplify(formula):
	if (ftype(formula) == VALUE_T):
		return formula
	elif (ftype(formula) == NOT_T):
		child = simplify(formula[1])
		if (ftype(child) == VALUE_T):
			return not child
		else:
			return ['notprop', child]
	elif (ftype(formula) == OR_T):
		child1 = simplify(formula[1])
		child2 = simplify(formula[2])
		if (child1 == True or child2 == True):
			return True
		elif (child1 == False and child2 == False):
			return False
		else:
			return ['orprop', child1, child2]
	else:
		return residue

#def ag_reduce(Struct, cstate, formula_entry):
#	ctime = cstate["time"]
#	formtime = formula_entry[0]
#	formula = formula_entry[1]
#	formtype = ftype(formula)
#	if (formtype == EXP_T):
#		return ag_reduce(Struct, cstate, (formtime, formula[1]))
#	elif (formtype == VALUE_T):
#		return formula
#	elif (formtype == PROP_T):
#		if (cstate[formula[1]]):
#			return True
#		else:
#			return False
#	elif (formtype == NPROP_T):
#		if (cstate[formula[1]]):
#			return False
#		else:
#			return True
#	elif (formtype == NOT_T):
#		child = simplify(ag_reduce(Struct, cstate, (formtime, formula[1])))
#		if (ftype(child) == VALUE_T):
#			return not child
#		else:
#			return ['notprop', child]
#	elif (formtype == AND_T):
#		child1 = ag_reduce(Struct, cstate, (formtime, formula[1]))
#		child2 = ag_reduce(Struct, cstate, (formtime, formula[2]))
#		simp = simplify(['andprop', child1, child2])
#		if (ftype(simp) == VALUE_T):
#			return simp;
#	elif (formtype == OR_T):
#		child1 = ag_reduce(Struct, cstate, (formtime, formula[1]))
#
#		if (child1 == True):
#			return True
#		child2 = ag_reduce(Struct, cstate, (formtime, formula[2]))
#		if (child2 == True):
#			return True
#		elif (child1 == False and child2 == False):
#			return False
#		else:
#			return ['orprop', child1, child2]
#	elif (formtype == IMPLIES_T):
#		child1 = ag_reduce(Struct, cstate, (formtime, formula[1]))
#		if (child1 == False):
#			return True
#		child2 = ag_reduce(Struct, cstate, (formtime, formula[2]))
#		if (child2 == True):
#			return True
#		elif (child1 == True and child2 == False):
#			return False
#		else:
#			return ['impprop', child1, child2]
#	elif (formtype == EVENT_T): 
#		h = hbound(formula) + formtime
#		l = lbound(formula) + formtime
#		subStruct = Struct[get_tags(formula)]
#		sthist = subStruct.history
#		check = CInterval(l,h)
#		#
#		for i in reversed(sthist):
#			if i.intersects(check):
#				return True
#		if (subStruct.valid >= h):
#			return False
#		return formula
#	elif (formtype == ALWAYS_T):
#		h = hbound(formula) + formtime
#		l = lbound(formula) + formtime
#		subStruct = Struct[get_tags(formula)]
#		sthist = subStruct.history
#		check = CInterval(l,h)
#		#
#		alcheck = subStruct.alCheck(check)
#		if (alcheck == ALC_SATISFY):
#			return True
#		elif (alcheck == ALC_VIOLATE):
#			return False
#		else: # alcheck == ALC_ALIVE
#			return formula
#	elif (formtype == UNTIL_T): 
#		tags = get_tags(formula)
#		subStruct1 = Struct[tags[0]]
#		subStruct2 = Struct[tags[1]]
#		sthist1 = subStruct1.history
#		sthist2 = subStruct2.history
#		h = hbound(formula) + formtime
#		l = lbound(formula) + formtime
#		check = CInterval(l,h)
#		end = None
#		#done = True
#
#		for i in reversed(sthist2):
#			if i.intersects(check):
#				end = i.intersection(check).end
#				break	# find the most recent one
#		# didn't find P2 and past time
#		if (end is None and subStruct2.valid >= h):
#			return False
#		elif (end is None):
#			end = ctime
#
#		l = formtime	
#		h = end
#		check = CInterval(l,h)
#		alcheck = subStruct1.alCheck(check)
#
#		if (alcheck == ALC_SATISFY and subStruct2.valid >= h):
#			return True
#		elif (alcheck == ALC_VIOLATE):
#			return False
#		else: # alcheck == ALC_ALIVE or ALC_SAT and not found
#			return formula
#	elif (formtype == PEVENT_T):
#		h = formtime - lbound(formula)
#		l = formtime - hbound(formula)
#		subStruct = Struct[get_tags(formula)]
#		sthist = subStruct.history
#		check = CInterval(l,h)
#		#
#		for i in reversed(sthist):
#			if i.intersects(check):
#				return True
#		if subStruct.valid >= h:
#			return False
#		return formula
#	elif (formtype == PALWAYS_T):
#		h = formtime - lbound(formula)
#		l = formtime - hbound(formula)
#		subStruct = Struct[get_tags(formula)]
#		sthist = subStruct.history
#		check = CInterval(l,h)
#		#
#		alcheck = subStruct.alCheck(check)
#		if (alcheck == ALC_SATISFY):
#			return True
#		elif (alcheck == ALC_VIOLATE):
#			return False
#		else: # alcheck == ALC_ALIVE
#			return formula
#	elif (formtype == SINCE_T):
#		tags = get_tags(formula)
#		subStruct1 = Struct[tags[0]]
#		subStruct2 = Struct[tags[1]]
#		sthist1 = subStruct1.history
#		sthist2 = subStruct2.history
#		h = formtime - lbound(formula)
#		l = formtime - hbound(formula)
#		start = None
#		check = CInterval(l,h)
#		#
#		#print "checking since at %s" % check
#		#print "eventhist: %s" % sthist2
#		for i in reversed(sthist2):
#			if i.intersects(check):
#				start = i.intersection(check).end
#				break	# find the most recent one
#		if (start is None and subStruct2.valid >= h):
#			return False
#		elif (start is None):
#			# haven't seen eventually yet, can't check always
#			return formula
#
#		l = start + PERIOD
#		h = formtime
#		check = CInterval(l,h)
#		alcheck = subStruct1.alCheck(check)
#
#		#print "checking always at %s" % check
#		#print "alwayshist: %s" % sthist1
#		if (alcheck == ALC_SATISFY or alcheck == ALC_ALIVE and subStruct2.valid >= h):
#			return True
#		elif (alcheck == ALC_VIOLATE):
#			return False
#		else: # alcheck == ALC_ALIVE or ALC_SAT and not found
#			return formula
#	else:
#		return INVALID_T

def tau(history, cptr):
	return int(history[cptr]['time'])

def dprint(string, lvl=0xFF):
#	print "DPRINT %s %d" % (string, lvl)
	if (DBG_MASK & lvl):
		print string
#######################################
##### Delay Functions
#######################################
def delay(formula):
	if (ftype(formula) == EXP_T):
		return delay(rchild(formula))
	elif (ftype(formula) == VALUE_T):
		return 0
	elif (ftype(formula) == PROP_T):
		return 0
	elif (ftype(formula) == NPROP_T):
		return 0
	elif (ftype(formula) == NOT_T):
		return delay(rchild(formula))
	elif (ftype(formula) == AND_T):
		return max(delay(lchild(formula)),delay(rchild(formula)))
	elif (ftype(formula) == OR_T):
		return max(delay(lchild(formula)),delay(rchild(formula)))
	elif (ftype(formula) == IMPLIES_T):
		return max(delay(lchild(formula)),delay(rchild(formula)))
	elif (ftype(formula) == EVENT_T): 
		return hbound(formula) + delay(rchild(formula))
	elif (ftype(formula) == ALWAYS_T):
		return hbound(formula) + delay(rchild(formula))
	elif (ftype(formula) == UNTIL_T): 
		return hbound(formula) + max(delay(untilP1(formula)),delay(untilP2(formula)))
	elif (ftype(formula) == PALWAYS_T):
		return delay(rchild(formula))
	elif (ftype(formula) == PEVENT_T):
		return delay(rchild(formula))
	elif (ftype(formula) == SINCE_T):
		return max(delay(untilP1(formula)),delay(untilP2(formula)))
	else:
		dprint("DELAY ERROR: Got unmatched AST node while building", DBG_ERROR);
		return None
	# shouldn't get here
	return None
def past_delay(formula):
	if (ftype(formula) == EXP_T):
		return past_delay(rchild(formula))
	elif (ftype(formula) == VALUE_T):
		return 0
	elif (ftype(formula) == PROP_T):
		return 0
	elif (ftype(formula) == NPROP_T):
		return 0
	elif (ftype(formula) == NOT_T):
		return past_delay(rchild(formula))
	elif (ftype(formula) == AND_T):
		return max(past_delay(lchild(formula)),past_delay(rchild(formula)))
	elif (ftype(formula) == OR_T):
		return max(past_delay(lchild(formula)),past_delay(rchild(formula)))
	elif (ftype(formula) == IMPLIES_T):
		return max(past_delay(lchild(formula)),past_delay(rchild(formula)))
	elif (ftype(formula) == EVENT_T): 
		return past_delay(rchild(formula))
	elif (ftype(formula) == ALWAYS_T):
		return past_delay(rchild(formula))
	elif (ftype(formula) == UNTIL_T): 
		return max(past_delay(untilP1(formula)),past_delay(untilP2(formula)))
	elif (ftype(formula) == PALWAYS_T):
		return hbound(formula) + past_delay(rchild(formula))
	elif (ftype(formula) == PEVENT_T):
		return hbound(formula) + past_delay(rchild(formula))
	elif (ftype(formula) == SINCE_T):
		return hbound(formula) + max(past_delay(untilP1(formula)),past_delay(untilP2(formula)))
	else:
		dprint("PAST-DELAY ERROR: Got unmatched AST node while building", DBG_ERROR);
		return None
	# shouldn't get here
	return None
def wdelay(formula):
	if (ftype(formula) == EXP_T):
		return wdelay(rchild(formula))
	elif (ftype(formula) == VALUE_T):
		return 0
	elif (ftype(formula) == PROP_T):
		return 0
	elif (ftype(formula) == NPROP_T):
		return 0
	elif (ftype(formula) == NOT_T):
		return wdelay(rchild(formula))
	elif (ftype(formula) == AND_T):
		return max(wdelay(lchild(formula)),wdelay(rchild(formula)))
	elif (ftype(formula) == OR_T):
		return max(wdelay(lchild(formula)),wdelay(rchild(formula)))
	elif (ftype(formula) == IMPLIES_T):
		return max(wdelay(lchild(formula)),wdelay(rchild(formula)))
	elif (ftype(formula) == EVENT_T): 
		return hbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == ALWAYS_T):
		return hbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == UNTIL_T): 
		return hbound(formula) + max(wdelay(untilP1(formula)),wdelay(untilP2(formula)))
	elif (ftype(formula) == PALWAYS_T):
		return -1*lbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == PEVENT_T):
		return -1*lbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == SINCE_T):
		return -1*lbound(formula) + max(wdelay(untilP1(formula)),wdelay(untilP2(formula)))
	else:
		dprint("DELAY ERROR: Got unmatched AST node while building", DBG_ERROR);
		return None
	# shouldn't get here
	return None
def mwdelay(formula):
	if (ftype(formula) == EXP_T):
		return wdelay(rchild(formula))
	elif (ftype(formula) == PROP_T):
		return 0
	elif (ftype(formula) == NPROP_T):
		return 0
	elif (ftype(formula) == NOT_T):
		return wdelay(rchild(formula))
	elif (ftype(formula) == AND_T):
		return max(wdelay(lchild(formula)),wdelay(rchild(formula)))
	elif (ftype(formula) == OR_T):
		return max(wdelay(lchild(formula)),wdelay(rchild(formula)))
	elif (ftype(formula) == IMPLIES_T):
		return max(wdelay(lchild(formula)),wdelay(rchild(formula)))
	elif (ftype(formula) == EVENT_T): 
		return hbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == ALWAYS_T):
		return lbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == UNTIL_T): 
		return hbound(formula) + max(wdelay(untilP1(formula)),wdelay(untilP2(formula)))
	elif (ftype(formula) == PALWAYS_T):
		return -1*hbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == PEVENT_T):
		return -1*lbound(formula) + wdelay(rchild(formula))
	elif (ftype(formula) == SINCE_T):
		return -1*lbound(formula) + max(wdelay(untilP1(formula)),wdelay(untilP2(formula)))
	else:
		dprint("DELAY ERROR: Got unmatched AST node while building", DBG_ERROR);
		return None
	# shouldn't get here
	return None
def nfdelay(formula):
	if (ftype(formula) == EXP_T):
		return nfdelay(rchild(formula))
	elif (ftype(formula) == PROP_T):
		return 0
	elif (ftype(formula) == NPROP_T):
		return 0
	elif (ftype(formula) == NOT_T):
		return nfdelay(rchild(formula))
	elif (ftype(formula) == AND_T):
		return max(nfdelay(lchild(formula)),nfdelay(rchild(formula)))
	elif (ftype(formula) == OR_T):
		return max(nfdelay(lchild(formula)),nfdelay(rchild(formula)))
	elif (ftype(formula) == IMPLIES_T):
		return max(nfdelay(lchild(formula)),nfdelay(rchild(formula)))
	elif (ftype(formula) == EVENT_T): 
		return nfdelay(rchild(formula))
	elif (ftype(formula) == ALWAYS_T):
		return nfdelay(rchild(formula))
	elif (ftype(formula) == UNTIL_T): 
		return max(nfdelay(untilP1(formula)),nfdelay(untilP2(formula)))
	elif (ftype(formula) == PALWAYS_T):
		if (not_future(formula)):
			return nfdelay(rchild(formula))
		return hbound(formula) + nfdelay(rchild(formula))
	elif (ftype(formula) == PEVENT_T):
		if (not_future(formula)):
			return nfdelay(rchild(formula))
		return hbound(formula) + nfdelay(rchild(formula))
	elif (ftype(formula) == SINCE_T):
		if (not_future(formula)):
			return max(nfdelay(untilP1(formula)),nfdelay(untilP2(formula)))
		return hbound(formula) + max(nfdelay(untilP1(formula)),nfdelay(untilP2(formula)))
	else:
		dprint("NESTED-FUTURE-DELAY ERROR: Got unmatched AST node while building", DBG_ERROR);
		return None
	# shouldn't get here
	return None

########## Interval Utils
# add interval to list
def addInterval(intv, structlist):
	if (len(structlist) > 0):
		last = structlist[-1]
	else:
		last = (None, None)
	#if (iEnd(last) >= iStart(int)):
	if (iStart(intv)-PERIOD <= iEnd(last)):
	#if (iEnd(last)+PERIOD >= iStart(int)):
		structlist[-1] = (iStart(last), iEnd(intv))
	else:
		structlist.append(intv)
# start a new interval tuple
def new_interval(start):
	return (start, None)

# end an existing interval tuple
def close_interval(interval, end):
	return (interval[0], end)

# check if interval is open (infinite)
def isopen_interval(interval):
	return interval[1] is None

# check if i in [l,h]
def in_closed_int(i, interval):
	return (i >= interval[0] and i <= interval[1])

# check if i in [l,h) 
def in_interval(i, interval):
	# could cut down to i>=i[0] and (i[1] is None or i <= i[1])
	if (interval[1] is None):
		return i >= interval[0]
	else:
		return i >= interval[0] and i < interval[1]
# make access to intervals a little more clear
def iEnd(interval):
	return interval[1]
def iStart(interval):
	return interval[0]

# order of intervals matters, only checking infinite on history
# do the intervals intersect?
def intersect_exists(test_i, history_i):
	if ((isopen_interval(history_i) or iStart(test_i) < iEnd(history_i)) 
		and iStart(history_i) <= iEnd(test_i)):
		return True
	else:
		return False

# get start point of intersection
def intersect_start(test_i, history_i):
	if int_intersect_exists(test_i, history_i):
		return max(iStart(test_i), iStart(history_i))
	return None

# is test subset of history
def subset(test_i, history_i):
	if ((iStart(history_i) <= iStart(test_i)) and
		(isopen_interval(history_i) or iEnd(test_i) < iEnd(history_i))):
		return True
	return False


########## Formula Utilities
# get leftmost child
def lchild(formula): 
	return formula[1]
# get rightmost child
def rchild(formula): 
	return formula[-1]
## formula children for (p1 U_i p2)
def untilP1(formula):
	return formula[-2]
def untilP2(formula):
	return formula[-1]
# get lower temporal bound
def lbound(formula):
	return formula[1]
# get higher temporal bound
def hbound(formula):
	return formula[2]
def rform(residue):
	return residue[1]
def rstep(residue):
	return residue[0]
