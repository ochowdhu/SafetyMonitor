/** residues.h -- keep residue stuff here */


#ifndef __RESIDUES_H
#define __RESIDUES_H

#include "formula.h"

typedef struct residue {
	int step;
	formula form;
} residue;

typedef struct {
	int start;
	int end;
} interval;

#endif
