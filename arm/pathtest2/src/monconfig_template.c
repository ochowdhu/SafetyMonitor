/* monconfig.c -- initialization code for configured stuff */


#include "monconfig.h"


const int ftype[NFORMULAS] = { PROP_T, PROP_T, PROP_T, UNTIL_T, NOT_T, OR_T, VALUE_T, VALUE_T};


/*@@@@ Generate simplify tables @@@@*/
/*
 const formula simplifyNot[NFORMULAS] = {};
 const formula simplifyOr[NFORMULAS][NFORMULAS] = {{},{},...,{}}
 const formula simplifyUntil[NFORMULAS][NFORMULAS] = {{},{},...,{}}
 const formula simplifySince[NFORMULAS][NFORMULAS] = {{},{},...,{}}
 *
 *
 * ex:
	const formula notForms[NFORMULAS] = {0, 0, 4, 0, 0, 0, 7, 6}; // NOT
 */

// structure table
resStructure theStruct[NSTRUCT];
// formula table
fNode formulas[NFORMULAS];
// buffer table
resbuf rbuffers[NSTRUCT];
interval ibuffers[NSTRUCT][NBUFLEN*2];
residue resbuffers[NSTRUCT][NBUFLEN];

// main list of residues
resbuf mainresbuf;
residue mainresbuffers[NBUFLEN];
																							
																							
/*@@@@ Generate build_formula(void) which fills in the formula table @@@@*/
// need to define INVALID in monconfig.h 
// we don't need theFormula anymore either -- should remove it from formula.h and here...
void build_formula(void) {
	// INVALID
	formulas[0].type = VALUE_T;
	formulas[0].val.value = INVALID;
	//formulas[0].theFormula = 0;
	// FALSE
	formulas[1].type = VALUE_T;
	formulas[1].val.value = TRUE;
	//formulas[1].theFormula = 1;
	// TRUE
	formulas[2].type = VALUE_T;
	formulas[2].val.value = FALSE;
	//formulas[2].theFormula = 2;

	/*@@@@ Fill in the rest of the formula here @@@@*/
 }

/*
 * ex:
 *
	// A
	formulas[0].type = PROP_T;
	formulas[0].val.propMask = MASK_A;
	formulas[0].theFormula = 0;
	// b U c
	formulas[3].type = UNTIL_T;
	formulas[3].val.t_children.hbound = 40;
	formulas[3].val.t_children.lbound = 0;
	formulas[3].val.t_children.lchild = FORM_B; //1;
	formulas[3].val.t_children.rchild = FORM_C; //2;
	//formulas[3].val.t_children.lchild = &formulas[1];
	//formulas[3].val.t_children.rchild = &formulas[2];
	formulas[3].theFormula = 3;
 */


/*@@@@ Generate build_struct(void) which fills in the struct table @@@@*/
////// build structures
////// ORDER MATTERS: struct should be built with smaller formulas at smaller offsets
void build_struct(void) {
	int i;
	// we'll put together mainresbuf here for now
	resbInit(&mainresbuf, NBUFLEN, mainresbuffers);

	
	for (i = 0; i < NSTRUCT; i++) {
		//rbuffers[i].size = formulas[resbuffers[i]->form].val.t_children.hbound;
		// should be able to put delay in formula struct so we can set the delay per-formula
		rbuffers[i].size = NBUFLEN;
		rbuffers[i].buf = resbuffers[i];
	}
	/*@@@@  Call initResStruct() for each structure (in the correct order) @@@@*/
	/* ex:
		// just need to build B and C
		initResStruct(&theStruct[0], FORM_B, FORM_DELAY, &rbuffers[0], &ibuffers[0][0], &ibuffers[0][1]);
		initResStruct(&theStruct[1], FORM_C, FORM_DELAY, &rbuffers[1], &ibuffers[1][0], &ibuffers[1][1]);
	*/
}

/*@@@@ incrStruct doesn't change, just drop it in @@@@*/
void incrStruct(int step) {
	// loop over struct (make sure struct is built smallest to largest...)
	int i, cres, eres;	
	for (i = 0; i < NSTRUCT; i++) {
		resStructure *cStruct = &theStruct[i];
		// add residue to structure
		rbInsert(cStruct->residues, step, cStruct->formula);
		// call reduce on all residues
		cres = cStruct->residues->start;
		eres = cStruct->residues->end;
		// loop over every residue
		while (cres != eres) {
			reduce(stGetRes(cStruct, cres));
			
			// increment
			cres = (cres + 1) % theStruct[i].residues->size;
		}
		// could clean up extra stuff that's past time, but shouldn't ever really have any if we size buffer right
	}
}
