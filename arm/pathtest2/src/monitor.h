/* monitor.h -- monitor header file
 * Putting all the actual monitoring functions here (reduce, etc)
 */
 
 
#ifndef __MONITOR_H
#define __MONITOR_H
 
#include "formula.h"
#include "residues.h"
#include "circbuf.h"


// get proposition value
#define getProp(m) (cstate & m)

extern volatile int cstate, nstate; // current/next start -- just a set of bits for now
extern volatile int estep, instep;

typedef struct {
	int ctime;
	int delay;
	formula formula;
	resbuf* residues;
	interval* ttime;
	interval* ftime;
} resStructure;

extern void initResStruct(resStructure* st, formula form, int delay, resbuf *res, interval *t, interval *f);
extern residue* stGetRes(resStructure *st, int pos);
extern void reduce(int step, residue *res);

//extern formula getForm(fNode n);
extern fNode getNode(formula f);
	
#endif 
