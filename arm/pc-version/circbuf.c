/* circbuf.c -- code for circbuf */


#include "circbuf.h"
#include <stdio.h>

void resbInit(resbuf *rb, int size, residue *array) {
	rb->size = size;
	rb->start = 0;
	rb->end = 0;
	rb->buf = array;
}

void fstackInit(formulaStack *fs, unsigned int size, formula* buf) {
	fs->size = size;
	fs->sp = 0;
	fs->stack = buf;
}
int rbFull(resbuf *rb) {
		return (rb->end + 1) % rb->size == rb->start;
}

void rbInsertP(resbuf *rb, residue *res) {
	rb->buf[rb->end] = *res;
	rb->end = (rb->end + 1) % rb->size;
	if (rb->end == rb->start) {
		rb->start = (rb->start + 1) % rb->size;	// full, move the start
	}
}
void rbInsert(resbuf *rb, int step, formula f) {
	rb->buf[rb->end].step = step;
	rb->buf[rb->end].form = f;
	// just see if circbuf is working...
	rb->end = (rb->end + 1) % rb->size;
	if (rb->end == rb->start) {
		rb->start = (rb->start + 1) % rb->size;	// full, move the start
	}
}

residue* rbGet(resbuf *rb, int pos) {
	//return &(rb->buf[(rb->start + pos) % rb->size]);
	return &(rb->buf[pos]);
}

void rbRemoveFirst(resbuf *rb) {
	rb->start = (rb->start + 1) % rb->size;
}

///////////// residue buffer above
///////////// interval buffer below
void ibInit(intbuf *ib, int size, intNode *array) {
	ib->size = size;
	ib->start = 0;
	ib->end = 0;
	ib->buf = array;
}

void inodebufInit(inodebuf* ib, int size, intNode *array) {
	ib->size = size;
	ib->start = 0;
	ib->end = 0;
	ib->buf = array;
}

void ibPush(intbuf *ib, int start, int end) {
	ib->buf[ib->end].ival.start = start;
	ib->buf[ib->end].ival.end = end;
	// just see if circbuf is working...
	ib->end = (ib->end + 1) % ib->size;
	if (ib->end == ib->start) {
		ib->start = (ib->start + 1) % ib->size;	// full, move the start
	}
}

/*interval* ibGet(intbuf *ib, int pos) {
		return &(ib->buf[(ib->start + pos) % ib->size]);
}*/
intNode* ibPop(intbuf *ib) {
	intNode* ret = &(ib->buf[ib->start]);
	ib->start = (ib->start + 1) % ib->size;	// full, move the start
	return ret;
}

void intRingInit(intring *ring, intbuf *pool) {
	ring->start->ival.start = -1;
	ring->start->ival.end = -1;
	ring->start->next = ring->end;
	ring->end->ival.start = -1;
	ring->end->ival.end = -1;
	ring->end->next = NULL;
	ring->pool = pool;
}

void intRingAdd(intNode *anchor, intNode *newring) {
	newring->next = anchor->next;
	anchor->next = newring;
}

void RingAddStep(int step, intring *ring) {
	intNode *it;
	it = ring->start;
	intNode *next;
	while (it != ring->end) {
		if (step > (*it).ival.end + 1) {
			next = ibPop(ring->pool);
			next->ival.start = step;
			next->ival.end = step;
			intRingAdd(it, next);
		}

	}
}
///////////////// interval stuff above
///////////////// stack below
int stackPush(formulaStack *fs, formula f) {
	if (fs->sp < fs->size-1) {
		fs->stack[++(fs->sp)] = f;
		return 1;
	}
	return 0;
}
formula stackPop(formulaStack *fs) {
	if (fs->sp <= 0) {
		return 0;
	}
	fs->sp--;
	return fs->stack[fs->sp+1];
	return 0;
}
void stackDec(formulaStack *fs) {
	if (fs->sp > 0) {
		(fs->sp)--;
	}
	return;
}
int stackEmpty(formulaStack *fs) {
	return (fs->sp <= 0);
}
formula stackPeek(formulaStack *fs) {
	return fs->stack[fs->sp];
}
void stackReset(formulaStack *fs) {
	fs->sp = 0;
	// helpful to debug, don't need to acually erase
	/*int i = 0; 
	for (i = 0; i < fs->size; i++) {
		fs->stack[i] = 0;
	}*/
}
