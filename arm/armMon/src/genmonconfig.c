/** Auto Generated monitor configuration */
// FORMULA: ['impprop', ['prop', 'x0000'], ['eventprop', 0, 0, ['orprop', ['prop', 'x0001'], ['prop', 'x0002']]]]
#include "monconfig.h"
const int ftype[NFORMULAS] = { VALUE_T, VALUE_T, VALUE_T, PROP_T, PROP_T, PROP_T, OR_T, EVENT_T, IMPLIES_T, };
const formula notForms[NF_NOT] = {0,2,1,};
const formula orForms[NF_OR][NF_OR] = {{0,0,0,0,0,},
{0,1,2,4,5,},
{0,2,2,2,2,},
{0,4,2,0,6,},
{0,5,2,0,0,},
};
const formula andForms[NF_AND][NF_AND] = {{0,0,0,},
{0,1,1,},
{0,1,2,},
};
const formula impForms[NF_IMP][NF_IMP] = {{0,0,0,0,0,},
{0,2,2,2,2,},
{0,1,2,3,7,},
{0,0,2,0,8,},
{0,0,2,0,0,},
};
const formula POLICIES[NPOLICIES] = { 8, };
// build structures
void build_struct(void) {
int i,j;
fstackInit(&redStack, STACK_DEPTH, redStackBuf);
fstackInit(&redStackVals, STACK_DEPTH, redStackValsBuf);
fstackInit(&redStackDir, STACK_DEPTH, redStackDirBuf);
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
}initResStruct(&theStruct[0], 6, FORM_DELAY, &rbuffers[0], &intringbuffer[0][0], &intringbuffer[0][1]);
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
formulaStack redStackDir;
formula redStackBuf[STACK_DEPTH];
formula redStackValsBuf[STACK_DEPTH];
formula redStackDirBuf[STACK_DEPTH];
// interval stuff
intNode intnodebuf[NSTRUCT][2][NBUFLEN];
intNode *intnodebufP[NSTRUCT][2][NBUFLEN];
intbuf intbuffer[NSTRUCT][2];
intring intringbuffer[NSTRUCT][2];
// build formulas
void build_formula(void) {
formulas[0].type = VALUE_T;
formulas[0].val.value = 2;
formulas[0].notTag = 0;
formulas[0].orTag = 0;
formulas[0].andTag = 0;
formulas[0].impTag = 0;
formulas[1].type = VALUE_T;
formulas[1].val.value = 0;
formulas[1].notTag = 1;
formulas[1].orTag = 1;
formulas[1].andTag = 1;
formulas[1].impTag = 1;
formulas[2].type = VALUE_T;
formulas[2].val.value = 1;
formulas[2].notTag = 2;
formulas[2].orTag = 2;
formulas[2].andTag = 2;
formulas[2].impTag = 2;
formulas[3].type = PROP_T;
formulas[3].val.propMask = MASK_x0000;
formulas[3].notTag = -1;
formulas[3].orTag = -1;
formulas[3].andTag = -1;
formulas[3].impTag = 3;
formulas[4].type = PROP_T;
formulas[4].val.propMask = MASK_x0001;
formulas[4].notTag = -1;
formulas[4].orTag = 3;
formulas[4].andTag = -1;
formulas[4].impTag = -1;
formulas[5].type = PROP_T;
formulas[5].val.propMask = MASK_x0002;
formulas[5].notTag = -1;
formulas[5].orTag = 4;
formulas[5].andTag = -1;
formulas[5].impTag = -1;
formulas[6].type = OR_T;
formulas[6].val.children.lchild = 4;
formulas[6].val.children.rchild = 5;
formulas[6].notTag = -1;
formulas[6].orTag = -1;
formulas[6].andTag = -1;
formulas[6].impTag = -1;
formulas[6].structidx = 0;
formulas[7].type = EVENT_T;
formulas[7].notTag = -1;
formulas[7].orTag = -1;
formulas[7].andTag = -1;
formulas[7].impTag = 4;
formulas[7].val.t_children.lchild = 6;
formulas[7].val.t_children.lbound = 0;
formulas[7].val.t_children.hbound = 0;
formulas[8].type = IMPLIES_T;
formulas[8].val.children.lchild = 3;
formulas[8].val.children.rchild = 7;
formulas[8].notTag = -1;
formulas[8].orTag = -1;
formulas[8].andTag = -1;
formulas[8].impTag = -1;
}

void incrStruct(int step) { 
// loop over struct (make sure struct is built smallest to largest...) 
int i, cres, eres; residue *resp;
for (i = 0; i < NSTRUCT; i++) {
resStructure *cStruct = &theStruct[i];
// add residue to structure
rbInsert(cStruct->residues, step, cStruct->stformula);
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
