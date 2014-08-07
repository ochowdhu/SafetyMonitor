/* monconfig.c -- initialization code for configured stuff */


#include "monconfig.h"


const int ftype[NFORMULAS] = { PROP_T, PROP_T, PROP_T, UNTIL_T, NOT_T, OR_T, VALUE_T, VALUE_T};


const formula notForms[NFORMULAS] = {0, 0, 4, 0, 0, 0, 7, 6}; // NOT
const formula orForms[NFORMULAS][NFORMULAS] = {{0, 0, 0, 0, 0, 0, 6, 0},	// 0
																							 {0, 0, 0, 0, 0, 0, 6, 1},	// 1
																							 {0, 0, 0, 0, 0, 0, 6, 2},	// 2
																							 {0, 0, 0, 0, 5, 0, 6, 3},	// 3
																							 {0, 0, 0, 5, 0, 0, 6, 4},	// 4
																							 {0, 0, 0, 0, 0, 0, 6, 5},	// 5
																							 {6, 6, 6, 6, 6, 6, 6, 6},	// 6
																							 {0, 1, 2, 3, 4, 5, 6, 7}		// 7
																							};
const formula untilForms[NFORMULAS][NFORMULAS] = {{0, 0, 0, 0, 0, 0, 0, 0},	// 0
																									{0, 0, 3, 0, 0, 0, 0, 0},	// 1
																									{0, 3, 0, 0, 0, 0, 0, 0},	// 2
																									{0, 0, 0, 0, 0, 0, 0, 0},	// 3
																									{0, 0, 0, 0, 0, 0, 0, 0},	// 4
																									{0, 0, 0, 0, 0, 0, 0, 0},	// 5
																									{0, 0, 0, 0, 0, 0, 0, 0},	// 6
																									{0, 0, 0, 0, 0, 0, 0, 0}		// 7
																							};
const formula sinceForms[NFORMULAS][NFORMULAS] = {{0, 0, 0, 0, 0, 0, 0, 0},	// 0
																									{0, 0, 0, 0, 0, 0, 0, 0},	// 1
																									{0, 0, 0, 0, 0, 0, 0, 0},	// 2
																									{0, 0, 0, 0, 0, 0, 0, 0},	// 3
																									{0, 0, 0, 0, 0, 0, 0, 0},	// 4
																									{0, 0, 0, 0, 0, 0, 0, 0},	// 5
																									{0, 0, 0, 0, 0, 0, 0, 0},	// 6
																									{0, 0, 0, 0, 0, 0, 0, 0}		// 7
																							};
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
																							
/* Using a -> b U_0,1s c  for now so I can fill everything in and get an understanding */
/////// build formula
void build_formula(void) {
	// first, all leaves
	// TRUE
	formulas[6].type = VALUE_T;
	formulas[6].val.value = TRUE;
	formulas[6].theFormula = 6;
	// FALSE
	formulas[7].type = VALUE_T;
	formulas[7].val.value = FALSE;
	formulas[7].theFormula = 7;
	// A
	formulas[0].type = PROP_T;
	formulas[0].val.propMask = MASK_A;
	formulas[0].theFormula = 0;
	// B
	formulas[1].type = PROP_T;
	formulas[1].val.propMask = MASK_B;
	formulas[1].theFormula = 1;
	formulas[1].structidx = 0;
	// C
	formulas[2].type = PROP_T;
	formulas[2].val.propMask = MASK_C;
	formulas[2].theFormula = 2;
	formulas[2].structidx = 1;

	// b U c
	formulas[3].type = UNTIL_T;
	formulas[3].val.t_children.hbound = 40;
	formulas[3].val.t_children.lbound = 0;
	formulas[3].val.t_children.lchild = FORM_B; //1;
	formulas[3].val.t_children.rchild = FORM_C; //2;
	//formulas[3].val.t_children.lchild = &formulas[1];
	//formulas[3].val.t_children.rchild = &formulas[2];
	formulas[3].theFormula = 3;
	// a -> b U c ====> ~a || b U c
	// First
	// ~a
	formulas[4].type = NOT_T;
	formulas[4].val.child = FORM_A; // 0 &formulas[0];
	//formulas[4].val.child = &formulas[0];
	formulas[4].theFormula = 4;
	// then need ~a || b U c
	formulas[5].type = OR_T;
	formulas[5].val.children.lchild = FORM_NA; // 4
	formulas[5].val.children.rchild = FORM_BUC; // 3
	//formulas[5].val.children.lchild = &formulas[4];
	//formulas[5].val.children.rchild = &formulas[3];
	formulas[5].theFormula = 5;
}

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
	// just need to build B and C
	initResStruct(&theStruct[0], FORM_B, FORM_DELAY, &rbuffers[0], &ibuffers[0][0], &ibuffers[0][1]);
	initResStruct(&theStruct[1], FORM_C, FORM_DELAY, &rbuffers[1], &ibuffers[1][0], &ibuffers[1][1]);
}

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
		// could clean up extra stuff that's past time, but shouldn't ever really have any
	}
	
}
