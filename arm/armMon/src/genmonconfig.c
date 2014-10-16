/** Auto Generated monitor configuration */
// FORMULA: ['alwaysprop', 0, 10, ['prop', 'allF']]
#include "monconfig.h"
const int ftype[NFORMULAS] = { VALUE_T, VALUE_T, VALUE_T, PROP_T, ALWAYS_T, };
const formula notForms[NFORMULAS] = {0,2,1,0,0,};
const formula orForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,},
{0,1,2,3,4,},
{0,2,2,2,2,},
{0,3,2,0,0,},
{0,4,2,0,0,},
};
const formula andForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,},
{0,1,1,1,1,},
{0,1,2,3,4,},
{0,1,3,0,0,},
{0,1,4,0,0,},
};
const formula impForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,},
{0,2,2,2,2,},
{0,1,2,3,4,},
{0,0,0,0,0,},
{0,0,0,0,0,},
};
const formula POLICIES[NPOLICIES] = { 4, };
// build structures
void build_struct(void) {
int i,j;
fstackInit(&redStack, STACK_DEPTH, redStackBuf);
fstackInit(&redStackVals, STACK_DEPTH, redStackValsBuf);
for (i = 0; i < NPOLICIES; i++) { 
resbInit(&mainresbuf[i], NBUFLEN, mainresbuffers[i]);
}
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
resbuf mainresbuf[NPOLICIES];
residue mainresbuffers[NPOLICIES][NBUFLEN];
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
formulas[3].val.propMask = MASK_allF;
formulas[3].structidx = 0;
formulas[4].type = ALWAYS_T;
formulas[4].val.t_children.lchild = 3;
formulas[4].val.t_children.lbound = 0;
formulas[4].val.t_children.hbound = 10;
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
