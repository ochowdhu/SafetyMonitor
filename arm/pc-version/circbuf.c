/* circbuf.c -- code for circbuf */


#include "circbuf.h"


void resbInit(resbuf *rb, int size, residue *array) {
	rb->size = size+1;
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
	rb->end = (rb->end + 1) % rb->size;
	if (rb->end == rb->start) {
		rb->start = (rb->start + 1) % rb->size;	// full, move the start
	}
}

residue* rbGet(resbuf *rb, int pos) {
	return &(rb->buf[(rb->start + pos) % rb->size]);
}

void ibInit(intbuf *ib, int size, interval *array) {
	
}
void ibInsert(intbuf *ib, int step) {
	// not going to deal with this right now... just using residual list
	// need to sort so might as well think about data structures...
	return;
	/*char merge = 0, added = 0;
	interval* cint;
	int s = ib->start;
	while (s != ib->end) {
		cint = ibGet(ib, s);
		// check if extending...
		if (step-1 == cint->end) {
			cint->end = step;
			added = 1;
		} else if (step + 1 == cint->start) {
			if (added)
				merge = s;
			else {
				cint->start = step;
			}
		}
		// done extending, do we need to merge?
		if (merge) {
			
		}
		
		// no extend/merge -- add directly
	}*/
}



interval* ibGet(intbuf *ib, int pos) {
		return &(ib->buf[(ib->start + pos) % ib->size]);
}
