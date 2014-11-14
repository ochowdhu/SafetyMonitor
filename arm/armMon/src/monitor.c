/* monitor.c -- monitor code

*/

#include <stdio.h>
#include "monitor.h"
#include "monconfig.h"
#include "gendefs.h" // need FULL_LOGIC/USEINTS


#ifndef PC_MODE
// need this for checkCons to trigger failure -- should pull out fail/success functions
//#include "stm32f4_discovery.h"
#endif

#define BIT(n) (1 << (n))
#define AL_MASK BIT(0)
#define UN_MASK BIT(1)
#define TEMP_FALSE	0
#define TEMP_TRUE 	1
#define TEMP_RES		2

#define BIT_CLEAR(field, val) (field &= ~(val))
#define BIT_SET(field, val) (field |= (val))

#define MAX(a,b) (((a)>(b))?(a):(b))
#define MIN(a,b) (((a)<(b))?(a):(b))




volatile int cstate[NPROP/WORDSZ+(NPROP%WORDSZ!=0)], nstate[NPROP/WORDSZ+(NPROP%WORDSZ!=0)];
//volatile int cstate, nstate; // current/next start -- just a set of bits for now
volatile int estep, instep;
#ifdef PC_MODE
int numreduces;
#endif

int untilCheck(int step, residue* res);
int sinceCheck(int step, residue* res);
#ifdef FULL_LOGIC
int eventCheck(int step, residue* res);
int alwaysCheck(int step, residue* res);
int peventCheck(int step, residue* res);
int palwaysCheck(int step, residue* res);
int (*tempCheck[6]) (int step, residue *res) = {untilCheck, sinceCheck, eventCheck, alwaysCheck, peventCheck, palwaysCheck};
#else
int (*tempCheck[2]) (int step, residue *res) = {untilCheck, sinceCheck};
#endif

#ifdef PC_MODE
void printRing(intring* ring);
#endif

void initResStruct(resStructure* st, formula form, int delay, resbuf *res, intring *t, intring *f) {
	st->delay = delay;
	st->stformula = form;
	st->ctime = 0;
	st->residues = res;
	st->ttime = t;
	st->ftime = f;
}
residue* stGetRes(resStructure *st, int pos) {
	return &(st->residues->buf[pos]);
}

#ifdef PC_MODE
void printDS() {
	printf("stack: [");
	int sp = redStackDir.sp;
	while (sp > 0) {
		printf("%d ", redStackDir.stack[sp--]);
	}
	printf("]\n");
}
#endif

#ifdef ITERATIVE_RED
// Iterative Reduce, used to be itreduce -- now just using preprocessor
//void itreduce(int step, residue *res) {
void reduce(int step, residue *res) {
	//if (step < 0) { return FORM_TRUE;};
	fNode root;
	residue child1;
	formula fchild1, fchild2, newDir;
	int type;
	int rstep; 
	formula froot, prevNode;
	//prevNode = 0;
	// clear stacks
	stackReset(&redStack);
	stackReset(&redStackVals);
	stackReset(&redStackDir);
	// set up stuff
	rstep = res->step;
	stackPush(&redStack, res->form);
	stackPush(&redStackDir, DIR_DOWNLEFT);
	// Begin Loop
	while (stackEmpty(&redStack) == 0) {
		#ifdef PC_MODE
		numreduces++;
		#endif
		froot = stackPop(&redStack);
		type = ftype[froot];
		//printf("reducing %d (%d) from %d in D:[%d %d]\n", froot,type, prevNode, stackPeek(&redStackDir), redStackDir.stack[redStackDir.sp-1]);
		//printDS();
		//printf("reducing %d type %d in dir %d\n", froot, type, stackPeek(&redStackDir));
		switch (type) {
			//////////
			case (VALUE_T):
				stackPush(&redStackVals, froot);
				// flip direction to up, keep left/right
				stackFlipTop(&redStackDir);
				break;
			case (PROP_T):
				// get prop from formula table
				root = formulas[froot];
				if (getProp(root.val.propMask)) {
					stackPush(&redStackVals,FORM_TRUE);
				} else {
					stackPush(&redStackVals,FORM_FALSE);
				}
				// flip direction to up, keep left/right
				stackFlipTop(&redStackDir);
				break;
			case (NOT_T):
				root = formulas[froot];
				// not preserves direction
				newDir = stackPeek(&redStackDir);
				// check direction
				if (newDir & DIR_UP) {
					// this works for all three -- notForms gives correct True/False
					fchild1 = stackPop(&redStackVals);
					stackPush(&redStackVals, notForms[formulas[fchild1].notTag]);
				} else { // going down -- just push not and child to stack
					stackPush(&redStack, froot);
					stackPush(&redStack, root.val.child);
				}
				break;
			case (OR_T):
				root = formulas[froot];
				// check direction
				newDir = stackPop(&redStackDir);
				if (newDir == DIR_UPLEFT) {
					// check lchild and work on right if not done
					fchild1 = stackPeek(&redStackVals);
					if (fchild1 == FORM_TRUE) {
						// could do nothing, we'll pop and push for now
						stackPop(&redStackVals);
						stackPush(&redStackVals, FORM_TRUE);
						stackFlipTop(&redStackDir);
					} else { // need to do the right side
						stackPush(&redStack, froot);
						stackPush(&redStack, root.val.children.rchild);
						stackPush(&redStackDir, DIR_DOWNRIGHT);
					}
				} else if (newDir == DIR_UPRIGHT) {
					fchild1 = stackPop(&redStackVals);
					fchild2 = stackPop(&redStackVals);
					//stackPush(&redStackVals, orForms[fchild2*NFORMULAS+fchild1]);
					stackPush(&redStackVals, orForms[formulas[fchild2].orTag][formulas[fchild1].orTag]);
					stackFlipTop(&redStackDir);
				} else { // on the way down, push left
					stackPush(&redStack, froot);
					stackPush(&redStack, root.val.children.lchild);
					stackPush(&redStackDir, newDir);
					stackPush(&redStackDir, DIR_DOWNLEFT);
				}
				break;
			#ifdef FULL_LOGIC
			case (AND_T):
				root = formulas[froot];
				// check direction
				newDir = stackPop(&redStackDir);
				if (newDir == DIR_UPLEFT) {
					// check lchild and work on right if not done
					fchild1 = stackPeek(&redStackVals);
					if (fchild1 == FORM_FALSE) {
						// could do nothing, we'll pop and push for now
						stackPop(&redStackVals);
						stackPush(&redStackVals, FORM_FALSE);
						stackFlipTop(&redStackDir);
					} else { // need to do the right side
						stackPush(&redStack, froot);
						stackPush(&redStack, root.val.children.rchild);
						stackPush(&redStackDir, DIR_DOWNRIGHT);
					}
				} else if (newDir == DIR_UPRIGHT) {
					fchild1 = stackPop(&redStackVals);
					fchild2 = stackPop(&redStackVals);
					stackPush(&redStackVals, andForms[formulas[fchild2].andTag][formulas[fchild1].andTag]);
					stackFlipTop(&redStackDir);
				} else { // on the way down, push left
					stackPush(&redStack, froot);
					stackPush(&redStack, root.val.children.lchild);
					stackPush(&redStackDir, newDir);
					stackPush(&redStackDir, DIR_DOWNLEFT);
				}
				break;
			case (IMPLIES_T):
				root = formulas[froot];
				// check direction
				newDir = stackPop(&redStackDir);
				if (newDir == DIR_UPLEFT) {
					// check lchild and work on right if not done
					fchild1 = stackPeek(&redStackVals);
					if (fchild1 == FORM_FALSE) {
						// could do nothing, we'll pop and push for now
						stackPop(&redStackVals);
						stackPush(&redStackVals, FORM_TRUE);
						stackFlipTop(&redStackDir);
					} else { // need to do the right side
						stackPush(&redStack, froot);
						stackPush(&redStack, root.val.children.rchild);
						stackPush(&redStackDir, DIR_DOWNRIGHT);
					}
				} else if (newDir == DIR_UPRIGHT) {
					fchild1 = stackPop(&redStackVals);
					fchild2 = stackPop(&redStackVals);
					stackPush(&redStackVals, impForms[formulas[fchild2].impTag][formulas[fchild1].impTag]);
					stackFlipTop(&redStackDir);
				} else { // on the way down, push left
					stackPush(&redStack, froot);
					stackPush(&redStack, root.val.children.lchild);
					stackPush(&redStackDir, newDir);
					stackPush(&redStackDir, DIR_DOWNLEFT);
				}
				break;
			#endif
			case (UNTIL_T):
			case (SINCE_T):
			#ifdef FULL_LOGIC
			case (EVENT_T):
			case (ALWAYS_T):
			case (PEVENT_T):
			case (PALWAYS_T):
			#endif
			//case (UNTIL_T):
				// reusing type, saving memory space
				child1.step = rstep;
				child1.form = froot;
				//type = untilCheck(step, &child1);
				type = tempCheck[ftype[froot]-6](step, &child1); 
				if (type == TEMP_TRUE) {
					//res->form = FORM_TRUE;
					stackPush(&redStackVals, FORM_TRUE);
				} else if (type == TEMP_FALSE) {
					//res->form = FORM_FALSE;
					stackPush(&redStackVals, FORM_FALSE);
				} else {
					stackPush(&redStackVals, child1.form);
				}
				// no else, just return the residue unchanged
				stackFlipTop(&redStackDir);
				break;
			/*case (SINCE_T):
				child1.step = rstep;
				child1.form = froot;
				type = sinceCheck(step, &child1);
				if (type == TEMP_TRUE) {
					stackPush(&redStackVals, FORM_TRUE);
					//res->form = FORM_TRUE;
				} else if (type == TEMP_FALSE) {
					stackPush(&redStackVals, FORM_FALSE);
					//res->form = FORM_FALSE;
				} else {
					stackPush(&redStackVals, child1.form);
				}
				break;
				*/
			default:
				// shouldn't get here...
				break;

			////////////////
			//////////////
			//////////////
		}
		// leaving incase we want this for debug
		prevNode = froot;
	}
	//printf("finished red\n");
	res->form = stackPop(&redStackVals);
	stackReset(&redStack);
	stackReset(&redStackVals);
}
#else
// Recursive reduce, choose with preprocessor
void reduce(int step, residue *res) {
	fNode root;
	residue child1, child2;

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
			//root = formulas[res->form];
			// get child
			child1.step = res->step;
			child1.form = formulas[res->form].val.child;
			reduce(step, &child1);
			if (ftype[child1.form] == VALUE_T) {
				// Got a value, so our root node is [NOT VAL], so return correctly
				if (child1.form == FORM_TRUE)
					res->form = FORM_FALSE;
				else // child1.form == FORM_FALSE
					res->form = FORM_TRUE;
			// not fully reduced, return formula
			} else {
				// get formula from table
				res->form = notForms[formulas[child1.form].notTag];
			}
			return;
		case (OR_T):
			root = formulas[res->form];
			// grab child1
			child1.step = res->step;
			child1.form = root.val.children.lchild;
			//child1.form = root.val.children.lchild->theFormula;
			// grab child2
			child2.step = res->step;
			child2.form = root.val.children.rchild;
			//child2.form = root.val.children.rchild->theFormula;
			reduce(step, &child1);
			reduce(step, &child2);
			// we can optimize by reducing and checking individual steps
			// but for now let's just reduce both and call into the simplify table
			//res->form = orForms[child1.form*NFORMULAS+child2.form];
			res->form = orForms[formulas[child1.form].orTag][formulas[child2.form].orTag];
			return;
		case (EVENT_T):
		case (ALWAYS_T):
		case (PEVENT_T):
		case (PALWAYS_T):
		case (SINCE_T):
		case (UNTIL_T):
			// reusing type, saving memory space
			//type = untilCheck(step, res);
			type = tempCheck[froot-6](step, res);
			if (type == TEMP_TRUE)
				res->form = FORM_TRUE;
			else if (type == TEMP_FALSE)
				res->form = FORM_FALSE;
			// no else, just return the residue unchanged
			return;
		/*case (SINCE_T):
			type = sinceCheck(step, res);
			if (type == TEMP_TRUE)
				res->form = FORM_TRUE;
			else if (type == TEMP_FALSE)
				res->form = FORM_FALSE;
			// no else, just return the residue unchanged
			return;
		*/
		default:
			// shouldn't get here...
			return;
	}
}
#endif



#ifdef USEINTS
// untilCheck using Ints -- choose with preprocessor
//int untilCheckInt(int step, residue *res) {
int untilCheck(int step, residue *res) {
	int l, h; // temporal bounds
	int ls, le; // residue list loop pointers
	intring *beta, *alphat, *alphaf;
	intNode *nnb, *nna;
	resbuf *reslist;
	residue *resp;
	// interval vars
	int minRes = step, minTrue = -1;
	int islow, ishigh, aislow, aishigh;

	// get temporal bounds
	l = res->step + formulas[res->form].val.t_children.lbound;
	h = res->step + formulas[res->form].val.t_children.hbound;
	
	// No Beta Case
	beta = theStruct[formulas[formulas[res->form].val.t_children.rchild].structidx].ftime;
	for (nnb = beta->start; nnb->next != NULL; nnb = nnb->next) {
		if (nnb->ival.start <= l && nnb->ival.end >= h) {
			return TEMP_FALSE;
		// everything after this isn't in [l,h]
		} else if (nnb->ival.end < l) {
			break;
		}
	}

	// alpha not since possible beta case
	reslist = theStruct[formulas[formulas[res->form].val.t_children.rchild].structidx].residues;
	ls = reslist->start;
	le = reslist->end;
	while (ls != le) {
		resp = rbGet(reslist, ls);
		if (l <= resp->step && resp->step <= h && (resp->form != FORM_TRUE && resp->form != FORM_FALSE)) {
			minRes = resp->step;
			break;
		}
		// decrement to next item in list
		ls = (ls + 1) % reslist->size;
	}
	// Rest of cases mixed together
	// get true time interval lists
	alphat = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].ttime;
	alphaf = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].ftime;
	beta = theStruct[formulas[formulas[res->form].val.t_children.rchild].structidx].ttime;
	for (nnb = beta->start; nnb->next != NULL; nnb = nnb->next) {
		islow = MAX(nnb->ival.start,l);
		ishigh = MIN(nnb->ival.end, h);
		if (islow <= ishigh) {
			// //////////////////////////////////
			// Quick check of a not since b here
			if (minTrue == -1) {
				minTrue = MIN(islow, minRes)-1;
				for (nna = alphaf->start; nna->next != NULL; nna = nna->next) {
					aislow = MAX(nna->ival.start, res->step);
					aishigh = MIN(nna->ival.end, minTrue);
					if (aislow <= aishigh) {
						return TEMP_FALSE;
					}
				}
			}
			/////////////////////////////////////////
			for (nna = alphat->start; nna->next != NULL; nna = nna->next) {
				if (nna->ival.start <= res->step && nna->ival.end >= islow-1) {
					return TEMP_TRUE;
				}
			}
			if (islow <= res->step && res->step <= ishigh) {
				return TEMP_TRUE;
			}
		}
	}
	return TEMP_RES;
}
#else
// residue list untilCheck -- choose with preprocessor
int untilCheck(int step, residue* res) {
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
	a_until = step;	// if we don't fill a_u then everything is true or we didn't get the value yet...
	b_alive = -1;
	b_actual = -1;
	b_none = -1;
	temp_bits = 0;
	BIT_SET(temp_bits, (AL_MASK) );
	
	////////////////////////////////////////////////
	// loop over alpha list	
	reslist = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].residues;
	//reslist = theStruct[formulas[res->form].val.t_children.lchild->structidx].residues;
	ls = reslist->start;
	le = reslist->end;
	while (ls != le) {
		resp = rbGet(reslist, ls);
		if (resp->step > h) {
			break;
		}
		// Already guaranteed <= h from above
		if (res->step <= resp->step) { 	// check alpha from res->step onwards
			// keep updating a_until with current val as long as we keep seeing true
			if (resp->form != FORM_TRUE) {
				// got a not true, set a_u and mask so we get minimum
				if (temp_bits & UN_MASK) {
					a_until = resp->step;
					BIT_CLEAR(temp_bits, UN_MASK);
				}
				// see false: set mask to stop updating a_until, and set a_alive if it's first false
				if (resp->form == FORM_FALSE) {
					// a_alive is first false we see
					a_alive = resp->step;
					break;
				}
			}
		}
		// increment to next item in list
		ls = (ls + 1) % reslist->size;
	}
	//////////////////////////////////////////////////
	// loop over beta list
	reslist = theStruct[formulas[formulas[res->form].val.t_children.rchild].structidx].residues;
	//reslist = theStruct[formulas[res->form].val.t_children.rchild->structidx].residues;
	ls = reslist->start;
	le = reslist->end;
	temp_bits = 0;
	BIT_SET(temp_bits, (AL_MASK) );
	if (step >= h) 
		b_none = 1;	// past time, looking for none now
	while (ls != le) {
		resp = rbGet(reslist, ls);
		if (resp->step > h) {
			break;
		}
		if (l <= resp->step) {
			// keep updating alive until we see a false (and unset none if we see something)
			if (resp->form != FORM_FALSE) { 
				if (temp_bits & AL_MASK) {
					b_alive = resp->step;
					b_none = 0;
					BIT_CLEAR(temp_bits, AL_MASK);
				}
				// got a true, set b_actual and stop looking for first true
				if (resp->form == FORM_TRUE) {
					b_actual = resp->step;
					break;
				} 
			}
		}
		// increment to next item in list
		ls = (ls + 1) % reslist->size;
	}
	
	/////////////////////////////////
	// Could just update res->form here instead of passing up to reduce...
	//printf("UNTILCHECK@%d: bactual: %d, au: %d, al: %d, bal: %d, bn: %d\n", instep, b_actual, a_until, a_alive, b_alive, b_none); 
	if (b_actual != -1 && a_until != -1 && b_actual <= a_until) {
		return TEMP_TRUE;
	} else if (b_alive != -1 && a_alive != -1 && a_alive < b_alive) {
		return TEMP_FALSE;
	} else if (b_none == 1) {
		return TEMP_FALSE;
	} else {
		return TEMP_RES;
	}
}
#endif

#ifdef USEINTS
// sinceCheck using ints -- choose with preprocessor
//int sinceCheckInt(int step, residue *res) {
int sinceCheck(int step, residue *res) {
	int l, h; // temporal bounds
	int ls, le; // residue list loop pointers
	intring *beta, *alphat, *alphaf;
	intNode *nnb, *nna;
	resbuf *reslist;
	residue *resp;
	// interval vars
	int maxRes = -1, maxTrue = -1;
	int islow, ishigh, aislow, aishigh;
	// get temporal bounds
	l = res->step - formulas[res->form].val.t_children.hbound;
	h = res->step - formulas[res->form].val.t_children.lbound;
	if (h < 1) {
		return TEMP_TRUE;
	}
	l = MAX(l,1); // step 1 is first step, don't look before this

	// No Beta case
	beta = theStruct[formulas[formulas[res->form].val.t_children.rchild].structidx].ftime;
	for (nnb = beta->start; nnb->next != NULL; nnb = nnb->next) {
		if (nnb->ival.start <= l && nnb->ival.end >= h) {
			return TEMP_FALSE;
		// everything after this isn't in [l,h]
		} else if (nnb->ival.end < l) {
			break;
		}
	}
	// alpha not since possible beta
	reslist = theStruct[formulas[formulas[res->form].val.t_children.rchild].structidx].residues;
	ls = reslist->end-1;
	if (ls < 0) ls = reslist->size-1;
	le = reslist->start-1;
	if (le < 0) le = reslist->size-1;
	while (ls != le) {
		resp = rbGet(reslist, ls);
		if (l <= resp->step && resp->step <= h && (resp->form != FORM_TRUE && resp->form != FORM_FALSE)) {
			maxRes = resp->step;
			break;
		}
		// decrement to next item in list
		ls = (ls - 1) % reslist->size;
		// looping backwards, so if we roll over bump to the top
		if (ls < 0) { ls = (reslist->size - 1); }
	}
	// Rest of cases mixed together
	// get true-time interval lists
	alphat = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].ttime;
	alphaf = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].ftime;
	beta = theStruct[formulas[formulas[res->form].val.t_children.rchild].structidx].ttime;
	for (nnb = beta->start; nnb->next != NULL; nnb = nnb->next) {
		islow = MAX(nnb->ival.start,l);
		ishigh = MIN(nnb->ival.end, h);
		if (islow <= ishigh) {
			// //////////////////////////////////
			// Quick check of a not since b here
			if (maxTrue == -1) {
				maxTrue = MAX(ishigh, maxRes)+1;
				for (nna = alphaf->start; nna->next != NULL; nna = nna->next) {
					aislow = MAX(nna->ival.start, maxTrue);
					aishigh = MIN(nna->ival.end, res->step);
					if (aislow <= aishigh) {
						return TEMP_FALSE;
					}
				}
			}
			/////////////////////////////////////////
			for (nna = alphat->start; nna->next != NULL; nna = nna->next) {
				if (nna->ival.start <= ishigh+1 && nna->ival.end >= res->step) {
					return TEMP_TRUE;
				}
			}
			if (islow <= res->step && ishigh >= res->step) {
				return TEMP_TRUE;
			}
		}
	}
	return TEMP_RES;
}
#else
// residue list sinceCheck -- choose with preprocessor
int sinceCheck(int step, residue* res) {
	/// we can do intervals
	/// instead of a circ buffer we'll just keep a straight array
	/// since we have to resort after every insert anyway
	int l, h, a_alive, a_until, b_alive, b_actual, temp_bits, b_none;
	int ls, le;
	resbuf* reslist;
	residue* resp;
	
	// get temporal bounds
	l = res->step - formulas[res->form].val.t_children.hbound;
	h = res->step - formulas[res->form].val.t_children.lbound;
	l = MAX(l,1); // step 1 is first step, don't look before this
	h = MAX(h,1);
	
	// initialize everything
	a_alive = -1;
	a_until = res->step+1;
	b_alive = -1;
	b_actual = -1;
	b_none = -1;
	temp_bits = 0;
	BIT_SET(temp_bits, (AL_MASK | UN_MASK) );
	
	////////////////////////////////////////////////
	// loop over alpha list	
	reslist = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].residues;
	//reslist = theStruct[formulas[res->form].val.t_children.lchild->structidx].residues;
	le = reslist->start-1;
	if (le < 0) le = reslist->size-1;
	ls = reslist->end-1;
	if (ls < 0) ls = reslist->size - 1;
	while (ls != le) {
		resp = rbGet(reslist, ls);
		if (resp->step < l) {
			break;
		}
		//printf("since looping alpha at step %d\n", resp->step);
		// Already guaranteed >= l from above
		if (res->step >= resp->step) { 	// check alpha up to res->step
			// keep updating a_until with current val as long as we keep seeing true
			if (resp->form == FORM_TRUE && (temp_bits & UN_MASK)) {
				a_until = resp->step;
				// see false: set mask to stop updating a_until, and set a_alive if it's first false
			}	else if (resp->form == FORM_FALSE) {
				BIT_CLEAR(temp_bits, UN_MASK);
				// a_alive is first false we see
				if (temp_bits & AL_MASK) {
					a_alive = resp->step;
					BIT_CLEAR(temp_bits, AL_MASK);
				}
			} else if (!temp_bits) {
				break;	// got both values, done checking
			} else {
				// not True or already not until, no more until
				BIT_CLEAR(temp_bits, UN_MASK);
			}
		}
		// decrement to next item in list
		ls = (ls - 1) % reslist->size;
		// looping backwards, so if we roll over bump to the top
		if (ls < 0) { ls = (reslist->size - 1); }
	}
	//////////////////////////////////////////////////
	// loop over beta list
	reslist = theStruct[formulas[formulas[res->form].val.t_children.rchild].structidx].residues;
	//reslist = theStruct[formulas[res->form].val.t_children.rchild->structidx].residues;
	ls = reslist->end-1;
	if (ls < 0) ls = reslist->size-1;
	le = reslist->start-1;
	if (le < 0) le = reslist->size-1;

	temp_bits = 0;
	BIT_SET(temp_bits, (AL_MASK | UN_MASK) );
	if (step >= h) 
		b_none = 1;	// past time, looking for none now
	while (ls != le) {
		resp = rbGet(reslist, ls);
		if (resp->step < l) {
			break;
		}
		//printf("since looping beta at step %d\n", resp->step);
		if (resp->step <= h) {
			// keep updating alive until we see a false (and unset none if we see something)
			if (resp->form != FORM_FALSE && (temp_bits & AL_MASK)) {
				b_alive = resp->step;
				b_none = 0;
				BIT_CLEAR(temp_bits, AL_MASK);
			// got a true, set b_actual and stop looking for first true
			} 
			if (resp->form == FORM_TRUE && (temp_bits & UN_MASK)) {
					b_actual = resp->step;
					BIT_CLEAR(temp_bits, UN_MASK);
			} 
			if (!temp_bits) {
				break;	// got all three values, done searching
			} // no else...
		}
		// decrement to next item in list
		ls = (ls - 1) % reslist->size;
		// looping backwards, so if we roll over bump to the top
		if (ls < 0) { ls = (reslist->size - 1); }
	}
	
	/////////////////////////////////
	// Could just update res->form here instead of passing up to reduce...
	if (b_actual != -1 && a_until != -1 && b_actual+1 >= a_until) {
		return TEMP_TRUE;
	} else if (b_alive != -1 && a_alive != -1 && a_alive > b_alive) {
		return TEMP_FALSE;
	} else if (b_none == 1) {
		return TEMP_FALSE;
	} else {
		return TEMP_RES;
	}
}
#endif

#ifdef FULL_LOGIC
#ifdef USEINTS
int eventCheck(int step, residue* res) {
	int l, h; // temporal bounds
	intring *beta; 
	intNode *nnb;
	//resbuf *reslist;
	//residue *resp;
	// interval vars
	int islow, ishigh;


	// get temporal bounds
	l = res->step + formulas[res->form].val.t_children.lbound;
	h = res->step + formulas[res->form].val.t_children.hbound;
	//
	// True case
	beta = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].ttime;
	for (nnb = beta->start; nnb->next != NULL; nnb = nnb->next) {
		// intervals intersect if max of high and min of low make a non-empty interval
		islow = MAX(nnb->ival.start, l);
		ishigh = MIN(nnb->ival.end, h);
		if (islow <= ishigh) {
			return TEMP_TRUE;
		} else if (nnb->ival.end < l) {
			break;
		}
	}
	// No Beta Case
	beta = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].ftime;
	for (nnb = beta->start; nnb->next != NULL; nnb = nnb->next) {
		// fail if false is a superset of check range (can't possibly be true)
		if (nnb->ival.start <= l && nnb->ival.end >= h) {
			return TEMP_FALSE;
		// everything after this isn't in [l,h]
		} else if (nnb->ival.end < l) {
			break;
		}
	}
	return TEMP_RES;
}
#else
#endif
#ifdef USEINTS
int alwaysCheck(int step, residue* res) {
	int l, h; // temporal bounds
	intring *beta; 
	intNode *nnb;
	//resbuf *reslist;
	//residue *resp;
	// interval vars
	int islow, ishigh;

	// get temporal bounds
	l = res->step + formulas[res->form].val.t_children.lbound;
	h = res->step + formulas[res->form].val.t_children.hbound;
	// False case
	// any false intersects with [l,h] is false
	beta = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].ftime;
	for (nnb = beta->start; nnb->next != NULL; nnb = nnb->next) {
		// intervals intersect if max of high and min of low make a non-empty interval
		islow = MAX(nnb->ival.start, l);
		ishigh = MIN(nnb->ival.end, h);
		if (islow <= ishigh) {
			return TEMP_FALSE;
		} else if (nnb->ival.end < l) {
			break;
		}

	}
	// True case 
	// need to find an interval that is a superset of [l,h]
	beta = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].ttime;
	for (nnb = beta->start; nnb->next != NULL; nnb = nnb->next) {
		// fail if false is a superset of check range (can't possibly be true)
		if (nnb->ival.start <= l && nnb->ival.end >= h) {
			return TEMP_TRUE;
		// everything after this isn't in [l,h]
		} else if (nnb->ival.end < l) {
			break;
		}
	}
	return TEMP_RES;
}
#else
#endif
#ifdef USEINTS
int peventCheck(int step, residue* res) {
	int l, h; // temporal bounds
	intring *beta; 
	intNode *nnb;
	//resbuf *reslist;
	//residue *resp;
	// interval vars
	int islow, ishigh;


	// get temporal bounds
	l = res->step - formulas[res->form].val.t_children.hbound;
	h = res->step - formulas[res->form].val.t_children.lbound;
	// cheat to handle initialization -- everything before the trace works
	if (h < 1) {
		return TEMP_TRUE;
	}
	l = MAX(l,1); // step 1 is first step, don't look before this
	
	// True case
	beta = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].ttime;
	for (nnb = beta->start; nnb->next != NULL; nnb = nnb->next) {
		// intervals intersect if max of high and min of low make a non-empty interval
		islow = MAX(nnb->ival.start, l);
		ishigh = MIN(nnb->ival.end, h);
		if (islow <= ishigh) {
			return TEMP_TRUE;
		} else if (nnb->ival.end < l) {
			break;
		}

	}
	// No Beta Case
	beta = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].ftime;
	for (nnb = beta->start; nnb->next != NULL; nnb = nnb->next) {
		// fail if false is a superset of check range (can't possibly be true)
		if (nnb->ival.start <= l && nnb->ival.end >= h) {
			return TEMP_FALSE;
		// everything after this isn't in [l,h]
		} else if (nnb->ival.end < l) {
			break;
		}
	}
	return TEMP_RES;
}
#else
#endif
#ifdef USEINTS
int palwaysCheck(int step, residue* res) {
	int l, h; // temporal bounds
	intring *beta; 
	intNode *nnb;
	//resbuf *reslist;
	//residue *resp;
	// interval vars
	int islow, ishigh;

	// get temporal bounds
	l = res->step - formulas[res->form].val.t_children.hbound;
	h = res->step - formulas[res->form].val.t_children.lbound;
	if (h < 1) {
		return TEMP_TRUE;
	}
	l = MAX(l,1); // step 1 is first step, don't look before this

	// False case
	// any false intersects with [l,h] is false
	beta = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].ftime;
	for (nnb = beta->start; nnb->next != NULL; nnb = nnb->next) {
		// intervals intersect if max of high and min of low make a non-empty interval
		islow = MAX(nnb->ival.start, l);
		ishigh = MIN(nnb->ival.end, h);
		if (islow <= ishigh) {
			return TEMP_FALSE;
		} else if (nnb->ival.end < l) {
			break;
		}

	}
	// True case 
	// need to find an interval that is a superset of [l,h]
	beta = theStruct[formulas[formulas[res->form].val.t_children.lchild].structidx].ttime;
	for (nnb = beta->start; nnb->next != NULL; nnb = nnb->next) {
		// fail if false is a superset of check range (can't possibly be true)
		if (nnb->ival.start <= l && nnb->ival.end >= h) {
			return TEMP_TRUE;
		// everything after this isn't in [l,h]
		} else if (nnb->ival.end < l) {
			break;
		}
	}
	return TEMP_RES;
}
#else
#endif
#endif // FULL_LOGIC


// We only call this when we start a new step, so no need to check
// that we're in a new one
void checkConsStep(resbuf *buf, int i) {
	residue* cresp;
	int start, end;
	
	// got rid of the loop, just check the first entry (should never need more than this)
	// loop incase we got delayed somehow
	// could just check delay of start (since we never need to check more than one entry)
	start = buf->start;
	end = buf->end;
	if (start != end) {		// not empty
		cresp = rbGet(buf, start);						// get first residue in list
		if ((cresp->step + FORM_DELAY) <= instep) {		// if it's old enough, we'll check it
			reduce(instep, cresp);
			//printf("reduced <%d,%d>@%d\n", cresp->step, cresp->form, instep);
			if (cresp->form == FORM_TRUE) {
				stepSatisfy();
				#ifdef PC_MODE
				rbSafeRemove(buf, start);
				#endif
			} else if (cresp->form == FORM_FALSE) {
				traceViolate(i);
				#ifdef PC_MODE
				rbSafeRemove(buf, start);
				#endif
			} else {	// not possible...
				traceFail();
				// LEDS?
			}
		}
	}
}

// Loop version -- shouldn't be necessary since we run checkCons every step, but keeping it around just incase
void checkConsStepLoop(resbuf *buf) {
	residue* cresp;
	int start, end;
	// don't think we need this loop, but want to debug with it first
	// loop incase we got delayed somehow
	// could just check delay of start (since we never need to check more than one entry)
	start = buf->start;
	end = buf->end;
	while (start != end) {
		cresp = rbGet(buf, start);
		if ((cresp->step + FORM_DELAY) <= instep) {
			reduce(estep, cresp);
			if (cresp->form == FORM_TRUE) {
				stepSatisfy();
				rbSafeRemove(buf, start);
			} else if (cresp->form == FORM_FALSE) {
				traceViolate(0); // need to pass this policy, but we don't use it right now
				rbSafeRemove(buf, start);
			} else {	// not possible...
				traceFail();
			}
			estep++;
		} else {
			// mainresbuf is ordered, later residues can't be from earlier
			break;
		}
		start = (start + 1) % buf->size;
	}
}


#ifdef PC_MODE
void printRing(intring *ring) {
	intNode *n;
	printf("printing ring...\n");
	for (n = ring->start; n->next != NULL; n = n->next) {
		printf("[%d,%d]  ", n->ival.start, n->ival.end);
	}
	printf("\n");
}
#endif

fNode getNode(formula f) {
	return formulas[0];
}
