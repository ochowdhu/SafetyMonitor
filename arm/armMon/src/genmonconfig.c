/** Auto Generated monitor configuration */
// FORMULA: ['andprop', ['prop', 'a'], ['eventprop', 0, 5, ['prop', 'b']]]
#include "monconfig.h"
const int ftype[NFORMULAS] = { VALUE_T, VALUE_T, VALUE_T, EVENT_T, PROP_T, PROP_T, AND_T, };
const formula notForms[NFORMULAS] = {0,2,1,0,0,0,0,};
const formula orForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,0,},
{0,1,2,3,4,5,6,},
{0,2,2,2,2,2,2,},
{0,3,2,0,0,0,0,},
{0,4,2,0,0,0,0,},
{0,5,2,0,0,0,0,},
{0,6,2,0,0,0,0,},
};
const formula andForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,0,},
{0,1,1,1,1,1,1,},
{0,1,2,3,4,5,6,},
{0,1,3,0,0,0,0,},
{0,1,4,6,0,0,0,},
{0,1,5,0,0,0,0,},
{0,1,6,0,0,0,0,},
};
const formula impForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,0,},
{0,2,2,2,2,2,2,},
{0,1,2,3,4,5,6,},
{0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,},
};
// build structures
void build_struct(void) {
int i,j;
fstackInit(&redStack, STACK_DEPTH, redStackBuf);
fstackInit(&redStackVals, STACK_DEPTH, redStackValsBuf);
resbInit(&mainresbuf, NBUFLEN, mainresbuffers);
for (i = 0; i < NSTRUCT; i++) { 
resbInit(&rbuffers[i], NBUFLEN, resbuffers[i]); 
for (j = 0; j < NBUFLEN; j++) {
// maybe memset the intnodebufs to 0, we'll see...
intnodebufP[i][0][j] = &intnodebuf[i][0][j];intnodebufP[i][1][j] = &intnodebuf[i][1][j];
}
ibInit(&intbuffer[i][0], NBUFLEN, intnodebufP[i][0]);
ibInit(&intbuffer[i][1], NBUFLEN, intnodebufP[i][1]);
intRingInit(&intringbuffer[i][0], &intbuffer[i][0]);
intRingInit(&intringbuffer[i][1], &intbuffer[i][1]);
}initResStruct(&theStruct[0], 5, FORM_DELAY, &rbuffers[0], &intringbuffer[0][0], &intringbuffer[0][1]);
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
// iterative stack stuff
formulaStack redStack;
formulaStack redStackVals;
formula redStackBuf[STACK_DEPTH];
formula redStackValsBuf[STACK_DEPTH];
// interval stuff
intNode intnodebuf[NSTRUCT][2][NBUFLEN];
intNode *intnodebufP[NSTRUCT][2][NBUFLEN];
intbuf intbuffer[NSTRUCT][2];
intring intringbuffer[NSTRUCT][2];
residue resbuffers[NSTRUCT][NBUFLEN];
// build formulas
void build_formula(void) {
formulas[0].type = VALUE_T;
formulas[0].val.value = INVALID;
formulas[1].type = VALUE_T;
formulas[1].val.value = FALSE;
formulas[2].type = VALUE_T;
formulas[2].val.value = TRUE;
formulas[3].type = EVENT_T;
formulas[3].val.t_children.lchild = 5;
formulas[3].val.t_children.lbound = 0;
formulas[3].val.t_children.hbound = 5;
formulas[3].structidx = 0;
formulas[4].type = PROP_T;
formulas[4].val.propMask = MASK_a;
formulas[5].type = PROP_T;
formulas[5].val.propMask = MASK_b;
formulas[5].structidx = 0;
formulas[6].type = AND_T;
formulas[6].val.children.lchild = 4;
formulas[6].val.children.rchild = 3;
}

void incrStruct(int step) { 
// loop over struct (make sure struct is built smallest to largest...) 
int i, cres, eres; residue *resp;
for (i = 0; i < NSTRUCT; i++) {
resStructure *cStruct = &theStruct[i];
// add residue to structure
rbInsert(cStruct->residues, step, cStruct->formula);
// call reduce on all residues
cres = cStruct->residues->start;
eres = cStruct->residues->end;
// loop over every residue
while (cres != eres) {
resp = stGetRes(cStruct, cres);
reduce(step, resp);
#ifdef USEINTS
if (resp->form == FORM_TRUE) { RingAddStep(resp->step, cStruct->ttime); rbSafeRemove(cStruct->residues, cres);}
else if (resp->form == FORM_FALSE) { RingAddStep(resp->step, cStruct->ftime); rbSafeRemove(cStruct->residues, cres);};
#endif
// increment
cres = (cres + 1) % theStruct[i].residues->size;
}
// could clean up extra stuff that's past time, but shouldn't ever really have any
}}
