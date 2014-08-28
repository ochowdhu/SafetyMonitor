/** Auto Generated monitor configuration */
#include "monconfig.h"
const int ftype[NFORMULAS] = { VALUE_T, VALUE_T, VALUE_T, PROP_T, NOT_T, PROP_T, PROP_T, UNTIL_T, OR_T, OR_T, };
const formula notForms[NFORMULAS] = {0,2,1,4,0,0,0,0,0,0,};
const formula orForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,0,0,0,0,},
{0,1,2,3,4,5,6,7,8,9,},
{0,2,2,2,2,2,2,2,2,2,},
{0,3,2,0,0,0,0,8,0,0,},
{0,4,2,0,0,0,0,9,0,0,},
{0,5,2,0,0,0,0,0,0,0,},
{0,6,2,0,0,0,0,0,0,0,},
{0,7,2,0,0,0,0,0,0,0,},
{0,8,2,0,0,0,0,0,0,0,},
{0,9,2,0,0,0,0,0,0,0,},
};
const formula untilForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,7,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
};
const formula sinceForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,},
};
// build structures
void build_struct(void) {
int i;
resbInit(&mainresbuf, NBUFLEN, mainresbuffers);
for (i = 0; i < NSTRUCT; i++) { rbuffers[i].size = NBUFLEN; rbuffers[i].buf = resbuffers[i]; }initResStruct(&theStruct[0], 5, FORM_DELAY, &rbuffers[0], &ibuffers[0][0], &ibuffers[0][1]);
initResStruct(&theStruct[1], 6, FORM_DELAY, &rbuffers[1], &ibuffers[1][0], &ibuffers[1][1]);
}

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
// build formulas
void build_formula(void) {
formulas[0].type = VALUE_T;
formulas[0].val.value = INVALID;
formulas[1].type = VALUE_T;
formulas[1].val.value = FALSE;
formulas[2].type = VALUE_T;
formulas[2].val.value = TRUE;
formulas[3].type = PROP_T;
formulas[3].val.propMask = MASK_a;
formulas[4].type = NOT_T;
formulas[4].val.child = 3;
formulas[5].type = PROP_T;
formulas[5].val.propMask = MASK_b;
formulas[5].structidx = 0;
formulas[6].type = PROP_T;
formulas[6].val.propMask = MASK_c;
formulas[6].structidx = 1;
formulas[7].type = UNTIL_T;
formulas[7].val.t_children.lchild = 5;
formulas[7].val.t_children.rchild = 6;
formulas[7].val.t_children.lbound = 0;
formulas[7].val.t_children.hbound = 5;
formulas[8].type = OR_T;
formulas[8].val.children.lchild = 3;
formulas[8].val.children.rchild = 7;
formulas[9].type = OR_T;
formulas[9].val.children.lchild = 4;
formulas[9].val.children.rchild = 7;
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
reduce(step, stGetRes(cStruct, cres));
// increment
cres = (cres + 1) % theStruct[i].residues->size;
}
// could clean up extra stuff that's past time, but shouldn't ever really have any
}}
