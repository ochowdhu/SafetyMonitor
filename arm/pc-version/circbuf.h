/* circbuf.h -- header for circular buffers 

*/

#ifndef __CIRCBUF_H
#define __CIRCBUF_H


// Circular buffers for residues:

#include "residues.h"

typedef struct resbuf {
	int size;
	int start;
	int end;
	residue *buf;
} resbuf;

typedef struct intNode {
	struct intNode *next;
	interval ival;
} intNode; 

typedef struct intbuf {
	int size;
	int start;
	int end;
//	interval* buf;
	intNode *buf;
} intbuf;

typedef struct intring {
	intNode* start;
	intNode* end;
	intbuf *pool;
} intring;


typedef struct formulaStack {
	unsigned int size;
	unsigned int sp;
	formula* stack;
} formulaStack;

extern void fstackInit(formulaStack *fs, unsigned int size, formula* buf);
extern int stackPush(formulaStack *fs, formula f);
extern formula stackPop(formulaStack *fs);
extern void stackDec(formulaStack *fs);
extern int stackEmpty(formulaStack *fs);
extern formula stackPeek(formulaStack *fs);
extern void stackReset(formulaStack *fs);

extern void resbInit(resbuf *rb, int size, residue *array);
extern int rbFull(resbuf *rb);
extern void rbInsertP(resbuf *rb, residue *res);
extern void rbInsert(resbuf *rb, int step, formula f);
extern residue* rbGet(resbuf *rb, int pos);
extern void rbRemoveFirst(resbuf *rb);

extern void ibInit(intbuf *ib, int size, intNode *array);
extern void ibInsert(intbuf *ib, int step);
extern interval* ibGet(intbuf *ib, int pos);
extern void ibPush(intbuf *ib, int start, int end);
extern intNode* ibPop(intbuf *ib);
//extern interval* ibGet(intbuf *ib, int pos);

extern void RingAddStep(int step, intring *ring);
extern void intRingInit(intring *ring, intbuf *pool);
extern void intRingAddFront(intring *ring, intNode * next);
extern void intRingRemove(intring *ring, intNode *prev, intNode* rem);
// essentially private
extern void intRingAdd(intNode *anchor, intNode *newring);
#endif
