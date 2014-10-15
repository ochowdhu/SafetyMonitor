/** Auto Generated monitor configuration */
// FORMULA: ['impprop', ['palwaysprop', 1, 2, ['prop', 'perF3']], ['alwaysprop', 3, 3, ['alwaysprop', 1, 2, ['prop', 'perF3']]]]
#include "monconfig.h"
const int ftype[NFORMULAS] = { VALUE_T, VALUE_T, VALUE_T, PROP_T, PALWAYS_T, ALWAYS_T, ALWAYS_T, IMPLIES_T, };
const formula notForms[NFORMULAS] = {0,2,1,0,0,0,0,0,};
const formula orForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,0,0,},
{0,1,2,3,4,5,6,7,},
{0,2,2,2,2,2,2,2,},
{0,3,2,0,0,0,0,0,},
{0,4,2,0,0,0,0,0,},
{0,5,2,0,0,0,0,0,},
{0,6,2,0,0,0,0,0,},
{0,7,2,0,0,0,0,0,},
};
const formula andForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,0,0,},
{0,1,1,1,1,1,1,1,},
{0,1,2,3,4,5,6,7,},
{0,1,3,0,0,0,0,0,},
{0,1,4,0,0,0,0,0,},
{0,1,5,0,0,0,0,0,},
{0,1,6,0,0,0,0,0,},
{0,1,7,0,0,0,0,0,},
};
const formula impForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,0,0,},
{0,2,2,2,2,2,2,2,},
{0,1,2,3,4,5,6,7,},
{0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,7,0,},
{0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,},
};
const formula POLICIES[NPOLICIES] = { 7, };
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
}initResStruct(&theStruct[0], 3, FORM_DELAY, &rbuffers[0], &intringbuffer[0][0], &intringbuffer[0][1]);
initResStruct(&theStruct[1], 5, FORM_DELAY, &rbuffers[1], &intringbuffer[1][0], &intringbuffer[1][1]);
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
formulas[0].val.value = 2;
formulas[1].type = VALUE_T;
formulas[1].val.value = 0;
formulas[2].type = VALUE_T;
formulas[2].val.value = 1;
formulas[3].type = PROP_T;
formulas[3].val.propMask = MASK_perF3;
formulas[3].structidx = 0;
formulas[4].type = PALWAYS_T;
formulas[4].val.t_children.lchild = 3;
formulas[4].val.t_children.lbound = 1;
formulas[4].val.t_children.hbound = 2;
formulas[5].type = ALWAYS_T;
formulas[5].val.t_children.lchild = 3;
formulas[5].val.t_children.lbound = 1;
formulas[5].val.t_children.hbound = 2;
formulas[5].structidx = 1;
formulas[6].type = ALWAYS_T;
formulas[6].val.t_children.lchild = 5;
formulas[6].val.t_children.lbound = 3;
formulas[6].val.t_children.hbound = 3;
formulas[7].type = IMPLIES_T;
formulas[7].val.children.lchild = 4;
formulas[7].val.children.rchild = 6;
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
