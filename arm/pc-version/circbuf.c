/* circbuf.c -- code for circbuf */


#include "circbuf.h"
#include <stdio.h>
#define TRUE 1
#define FALSE 0



void resbInit(resbuf *rb, int size, residue *array) {
	rb->size = size;
	rb->start = 0;
	rb->end = 0;
	rb->buf = array;
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
void ibInit(intbuf *ib, int size, intNode **array) {
	ib->size = size;
	ib->start = 0;
	//ib->end = 0;
	ib->end = size-1;	// filled by pointing to good memory
	ib->buf = array;
}

void ibPush(intbuf *ib, intNode *n) {
	ib->buf[ib->end] = n;
	ib->end = (ib->end + 1) % ib->size;
	if (ib->end == ib->start) {
		ib->start = (ib->start + 1) % ib->size;	// full, move the start
	}
}
intNode* ibPop(intbuf *ib) {
	intNode* ret = ib->buf[ib->start];
	ib->start = (ib->start + 1) % ib->size;	// full, move the start
	return ret;
}

// //////////////////////////////
// intring stuff
void intRingInit(intring *ring, intbuf *pool) {
	ring->pool = pool;
	ring->start = ibPop(ring->pool);
	ring->end = ring->start;
	ring->start->ival.start = -1;
	ring->start->ival.end = -1;
	ring->start->next = NULL;
}

void intRingAdd(intNode *anchor, intNode *newring) {
	newring->next = anchor->next;
	anchor->next = newring;
}

void intRingAddFront(intring *ring, intNode *newring) {
	newring->next = ring->start;
	ring->start = newring;
}
void intRingRemove(intring* ring, intNode *prev, intNode* rem) {
	prev->next = rem->next;
	ibPush(ring->pool, rem);
}
void RingAddStep(int step, intring *ring) {
	intNode *it, *lastit;
	lastit = NULL;
	it = ring->start;
	intNode *next;
	char added = FALSE;
	while (it != ring->end) {
		// either newest so add and be done
		// or we already added it and are not merging
		if (step > (*it).ival.end + 1) {
			if (added == FALSE) {
				next = ibPop(ring->pool);
				next->ival.start = step;
				next->ival.end = step;
				if (lastit == NULL) {
					intRingAddFront(ring, next);
				} else {
					intRingAdd(lastit, next);
				}
				added = TRUE;
			}
			break;
		// extends current interval at the back
		// merge with previous if we added already
		} else if (step == (*it).ival.end + 1) {
			if (added == TRUE) {
				// MERGE -- put our start in last guy and delete 
				// current
				lastit->ival.start = (*it).ival.start;
				intRingRemove(ring, lastit, (it));
				break;
			// new, just extend and be done
			} else {
				(*it).ival.end = step;
				added = TRUE;
				break;
			}
		// if this extends the front, extend
		// this is the only add case that continues to check for merges
		} else if (step == (*it).ival.start - 1) {
				(*it).ival.start = step;
				added = TRUE;
		} else if ((*it).ival.start <= step && step <= ((*it).ival.end)) {
			// do nothing, already inside
			added = TRUE;
			break;
		}
		lastit = it;
		it = it->next;
	}
	// got to end and didn't add, so add it to the end
	// i.e. step < all intervals
	if (added == FALSE) {
		next = ibPop(ring->pool);
		next->ival.start = step;
		next->ival.end = step;
		if (lastit == NULL) {
			intRingAddFront(ring, next);
		} else {
			intRingAdd(lastit, next);
		}
	}
}
///////////////// interval stuff above
///////////////// FORMULA STACK STUFF
void fstackInit(formulaStack *fs, unsigned int size, formula* buf) {
	fs->size = size;
	fs->sp = 0;
	fs->stack = buf;
}
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
//// END FORMULA STACK STUFF
