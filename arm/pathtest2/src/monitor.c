/* monitor.c -- monitor code

*/

#include "monitor.h"
#include "monconfig.h"

#define BIT(n) (1 << (n))
#define AL_MASK BIT(0)
#define UN_MASK BIT(1)
#define TEMP_FALSE	0
#define TEMP_TRUE 	1
#define TEMP_RES		2

#define BIT_CLEAR(field, val) (field &= ~(val))
#define BIT_SET(field, val) (field |= (val))


volatile int cstate, nstate; // current/next start -- just a set of bits for now

int untilCheck(residue* res);
int sinceCheck(residue* res);

void initResStruct(resStructure* st, formula form, int delay, resbuf *res, interval *t, interval *f) {
	st->delay = delay;
	st->formula = form;
	st->ctime = 0;
	st->residues = res;
	st->ttime = t;
	st->ftime = f;
}
residue* stGetRes(resStructure *st, int pos) {
	return &(st->residues->buf[pos]);
}

void reduce(residue *res) {
	fNode root;
	residue child1, child2;
	// UNTIL/SINCE stuff -- moved to check functions
	//int a_alive, a_until, b_alive, b_until;
	//int l, h, ls, le;
	//residue* resp;
	//resbuf* reslist;
	//char temp_bits;
	
	int type = ftype[res->form];
	switch (type) {
		case (VALUE_T):
			return;
		case (PROP_T):
			// get prop from formula table
			root = formulas[res->form];
			if (getProp(root.val.propMask))
				res->form = FORM_TRUE;
			else 
				res->form = FORM_FALSE;
			return;
		case (NOT_T):
			root = formulas[res->form];
			// get child
			root = *(root.val.child);
			child1.step = res->step;
			child1.form = root.theFormula;
			reduce(&child1);
			if (ftype[child1.form] == VALUE_T) {
				// Got a value, so our root node is [NOT VAL], so return correctly
				if (child1.form == FORM_TRUE)
					res->form = FORM_FALSE;
				else // child1.form == FORM_FALSE
					res->form = FORM_TRUE;
			// not fully reduced, return formula
			} else {
				// get formula from table
				res->form = notForms[child1.form];
			}
			return;
		case (OR_T):
			root = formulas[res->form];
			// grab child1
			child1.step = res->step;
			child1.form = root.val.children.lchild->theFormula;
			// grab child2
			child2.step = res->step;
			child2.form = root.val.children.rchild->theFormula;
			reduce(&child1);
			reduce(&child2);
			// we can optimize by reducing and checking individual steps
			// but for now let's just reduce both and call into the simplify table
			res->form = orForms[child1.form][child2.form];
			return;
		case (UNTIL_T):
			// reusing type, saving memory space
			type = untilCheck(res);
			if (type == TEMP_TRUE)
				res->form = FORM_TRUE;
			else if (type == TEMP_FALSE)
				res->form = FORM_FALSE;
			// no else, just return the residue unchanged
			return;
		case (SINCE_T):
			type = sinceCheck(res);
			if (type == TEMP_TRUE)
				res->form = FORM_TRUE;
			else if (type == TEMP_FALSE)
				res->form = FORM_FALSE;
			// no else, just return the residue unchanged
			return;
		default:
			// shouldn't get here...
			return;
	}
}



int untilCheck(residue* res) {
	/// we can do intervals
	/// instead of a circ buffer we'll just keep a straight array
	/// since we have to resort after every insert anyway
	int l, h, a_alive, a_until, b_alive, b_actual, temp_bits, b_none;
	int ls, le;
	resbuf* reslist;
	residue* resp;
	
	// get temporal bounds
	l = res->step + formulas[res->form].val.t_children.lbound;
	h = res->step + formulas[res->form].val.t_children.hbound;
	
	// initialize everything
	a_alive = -1;
	a_until = res->step-1;
	b_alive = -1;
	b_actual = -1;
	b_none = -1;
	BIT_SET(temp_bits, (AL_MASK | UN_MASK) );
	
	////////////////////////////////////////////////
	// loop over alpha list	
	reslist = theStruct[formulas[res->form].val.t_children.lchild->structidx].residues;
	ls = reslist->start;
	le = reslist->end;
	while (ls != le) {
		resp = rbGet(reslist, ls);
		if (resp->step > h) {
			break;
		}
		// Already guaranteed <= h from above
		if (l <= resp->step) { 
			// keep updating a_until with current val as long as we keep seeing true
			if (resp->form == FORM_TRUE && (temp_bits & UN_MASK)) {
				a_until = resp->step;
				// see false: set mask to stop updating a_until, and set a_alive if it's first false
			}	else if (resp->form == FORM_FALSE) {
				BIT_CLEAR(temp_bits, UN_MASK);
				// a_alive is first false we see
				if (temp_bits & AL_MASK) {
					a_alive = rbGet(reslist, ls)->step;
					BIT_CLEAR(temp_bits, AL_MASK);
				}
			} else if (!temp_bits) {
				break;	// got both values, done checking
			} else {
				// not True or already not until, no more until
				BIT_CLEAR(temp_bits, UN_MASK);
			}
		}
		// increment to next item in list
		ls = (ls + 1) % reslist->size;
	}
	//////////////////////////////////////////////////
	// loop over beta list
	reslist = theStruct[formulas[res->form].val.t_children.rchild->structidx].residues;
	ls = reslist->start;
	le = reslist->end;
	BIT_SET(temp_bits, (AL_MASK | UN_MASK) );
	if (res->step >= h) 
		b_none = 1;	// past time, looking for none now
	while (ls != le) {
		resp = rbGet(reslist, ls);
		if (resp->step > h) {
			break;
		}
		if (l <= resp->step) {
			// keep updating alive until we see a false (and unset none if we see something)
			if (resp->form != FORM_FALSE && (temp_bits & AL_MASK)) {
				b_alive = resp->step;
				b_none = 0;
				BIT_CLEAR(temp_bits, AL_MASK);
			// got a true, set b_actual and stop looking for first true
			} else if (resp->form == FORM_TRUE && (temp_bits & UN_MASK)) {
					b_actual = rbGet(reslist, ls)->step;
					BIT_CLEAR(temp_bits, UN_MASK);
			} else if (!temp_bits) {
				break;	// got all three values, done searching
			} // no else...
		}
		// increment to next item in list
		ls = (ls + 1) % reslist->size;
	}
	
	/////////////////////////////////
	// Could just update res->form here instead of passing up to reduce...
	if (b_actual != -1 && a_until != -1 && b_actual-1 <= a_until) {
		return TEMP_TRUE;
	} else if (b_alive != -1 && a_alive != -1 && a_alive < b_actual) {
		return TEMP_FALSE;
	} else if (b_none) {
		return TEMP_FALSE;
	} else {
		return TEMP_RES;
	}
}


int sinceCheck(residue* res) {
	return TEMP_RES;
}
void test() {
	// should compile...
	return;
}

fNode getNode(formula f) {
	return formulas[0];
}
