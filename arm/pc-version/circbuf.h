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

typedef struct intbuf {
	int size;
	int start;
	int end;
	interval* buf;
} intbuf;

extern void resbInit(resbuf *rb, int size, residue *array);
extern int rbFull(resbuf *rb);
extern void rbInsertP(resbuf *rb, residue *res);
extern void rbInsert(resbuf *rb, int step, formula f);
extern residue* rbGet(resbuf *rb, int pos);
extern void rbRemoveFirst(resbuf *rb);

extern void ibInit(intbuf *ib, int size, interval *array);
extern void ibInsert(intbuf *ib, int step);
extern interval* ibGet(intbuf *ib, int pos);
#endif
