/** Auto Generated monitor configuration */
#include "monconfig.h"
const int ftype[NFORMULAS] = { VALUE_T, VALUE_T, VALUE_T, PROP_T, UNTIL_T, UNTIL_T, };
const formula notForms[NFORMULAS] = {0,2,1,0,0,0,};
const formula orForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,},
{0,1,2,3,4,5,},
{0,2,2,2,2,2,},
{0,3,2,0,0,0,},
{0,4,2,0,0,0,},
{0,5,2,0,0,0,},
};
const formula untilForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,},
{0,0,0,4,5,0,},
{0,0,0,0,0,0,},
{0,0,0,0,0,0,},
{0,0,0,0,0,0,},
{0,0,0,0,0,0,},
};
const formula sinceForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,},
{0,0,0,0,0,0,},
{0,0,0,0,0,0,},
{0,0,0,0,0,0,},
{0,0,0,0,0,0,},
{0,0,0,0,0,0,},
};
// build structures
void build_struct(void) {
int i;
fstackInit(&redStack, STACK_DEPTH, redStackBuf);
fstackInit(&redStackVals, STACK_DEPTH, redStackValsBuf);
resbInit(&mainresbuf, NBUFLEN, mainresbuffers);
for (i = 0; i < NSTRUCT; i++) { 
	resbInit(&rbuffers[i], NBUFLEN, resbuffers[i]); 
	ibInit(&intbuffer[i][0], NBUFLEN, intnodebuf[i][0]);
}
initResStruct(&theStruct[0], 3, FORM_DELAY, &rbuffers[0], &intringbuffer[0][0], &intringbuffer[0][1]);
initResStruct(&theStruct[1], 4, FORM_DELAY, &rbuffers[1], &intringbuffer[1][0], &intringbuffer[1][1]);
}

// structure table
resStructure theStruct[NSTRUCT];
// formula table
fNode formulas[NFORMULAS];
// buffer table
resbuf rbuffers[NSTRUCT];
//interval ibuffers[NSTRUCT][NBUFLEN*2];
residue resbuffers[NSTRUCT][NBUFLEN];
// interval table stuff
intNode intnodebuf[NSTRUCT][2][NBUFLEN];
intbuf intbuffer[NSTRUCT][2];
intring intringbuffer[NSTRUCT][2];
residue resbuffers[NSTRUCT][NBUFLEN];
// main list of residues
resbuf mainresbuf;
residue mainresbuffers[NBUFLEN];
// iterative stack stuff
formulaStack redStack;
formulaStack redStackVals;
formula redStackBuf[STACK_DEPTH];
formula redStackValsBuf[STACK_DEPTH];
// build formulas
void build_formula(void) {
formulas[0].type = VALUE_T;
formulas[0].val.value = INVALID;
formulas[1].type = VALUE_T;
formulas[1].val.value = FALSE;
formulas[2].type = VALUE_T;
formulas[2].val.value = TRUE;
formulas[3].type = PROP_T;
formulas[3].val.propMask = MASK_allF;
formulas[3].structidx = 0;
formulas[4].type = UNTIL_T;
formulas[4].val.t_children.lchild = 1;
formulas[4].val.t_children.rchild = 3;
formulas[4].val.t_children.lbound = 0;
formulas[4].val.t_children.hbound = 300;
formulas[4].structidx = 1;
formulas[5].type = UNTIL_T;
formulas[5].val.t_children.lchild = 1;
formulas[5].val.t_children.rchild = 4;
formulas[5].val.t_children.lbound = 0;
formulas[5].val.t_children.hbound = 100;
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
