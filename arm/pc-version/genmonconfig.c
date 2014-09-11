/** Auto Generated monitor configuration */
#include "monconfig.h"
const int ftype[NFORMULAS] = { VALUE_T, VALUE_T, VALUE_T, PROP_T, NOT_T, PROP_T, PROP_T, SINCE_T, PROP_T, PROP_T, SINCE_T, SINCE_T, OR_T, OR_T, };
const formula notForms[NFORMULAS] = {0,2,1,4,0,0,0,0,0,0,0,0,0,0,};
const formula orForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,1,2,3,4,5,6,7,8,9,10,11,12,13,},
{0,2,2,2,2,2,2,2,2,2,2,2,2,2,},
{0,3,2,0,0,0,0,0,0,0,0,12,0,0,},
{0,4,2,0,0,0,0,0,0,0,0,13,0,0,},
{0,5,2,0,0,0,0,0,0,0,0,0,0,0,},
{0,6,2,0,0,0,0,0,0,0,0,0,0,0,},
{0,7,2,0,0,0,0,0,0,0,0,0,0,0,},
{0,8,2,0,0,0,0,0,0,0,0,0,0,0,},
{0,9,2,0,0,0,0,0,0,0,0,0,0,0,},
{0,10,2,0,0,0,0,0,0,0,0,0,0,0,},
{0,11,2,0,0,0,0,0,0,0,0,0,0,0,},
{0,12,2,0,0,0,0,0,0,0,0,0,0,0,},
{0,13,2,0,0,0,0,0,0,0,0,0,0,0,},
};
const formula untilForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
};
const formula sinceForms[NFORMULAS][NFORMULAS] = {{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,7,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,11,0,0,0,},
{0,0,0,0,0,0,0,0,0,10,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
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
initResStruct(&theStruct[1], 6, FORM_DELAY, &rbuffers[1], &intringbuffer[1][0], &intringbuffer[1][1]);
initResStruct(&theStruct[2], 7, FORM_DELAY, &rbuffers[2], &intringbuffer[2][0], &intringbuffer[2][1]);
initResStruct(&theStruct[3], 8, FORM_DELAY, &rbuffers[3], &intringbuffer[3][0], &intringbuffer[3][1]);
initResStruct(&theStruct[4], 9, FORM_DELAY, &rbuffers[4], &intringbuffer[4][0], &intringbuffer[4][1]);
initResStruct(&theStruct[5], 10, FORM_DELAY, &rbuffers[5], &intringbuffer[5][0], &intringbuffer[5][1]);
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
formulas[3].type = PROP_T;
formulas[3].val.propMask = MASK_x;
formulas[4].type = NOT_T;
formulas[4].val.child = 3;
formulas[5].type = PROP_T;
formulas[5].val.propMask = MASK_p;
formulas[5].structidx = 0;
formulas[6].type = PROP_T;
formulas[6].val.propMask = MASK_q;
formulas[6].structidx = 1;
formulas[7].type = SINCE_T;
formulas[7].val.t_children.lchild = 5;
formulas[7].val.t_children.rchild = 6;
formulas[7].val.t_children.lbound = 0;
formulas[7].val.t_children.hbound = 5;
formulas[7].structidx = 2;
formulas[8].type = PROP_T;
formulas[8].val.propMask = MASK_r;
formulas[8].structidx = 3;
formulas[9].type = PROP_T;
formulas[9].val.propMask = MASK_t;
formulas[9].structidx = 4;
formulas[10].type = SINCE_T;
formulas[10].val.t_children.lchild = 8;
formulas[10].val.t_children.rchild = 9;
formulas[10].val.t_children.lbound = 0;
formulas[10].val.t_children.hbound = 5;
formulas[10].structidx = 5;
formulas[11].type = SINCE_T;
formulas[11].val.t_children.lchild = 7;
formulas[11].val.t_children.rchild = 10;
formulas[11].val.t_children.lbound = 0;
formulas[11].val.t_children.hbound = 5;
formulas[12].type = OR_T;
formulas[12].val.children.lchild = 3;
formulas[12].val.children.rchild = 11;
formulas[13].type = OR_T;
formulas[13].val.children.lchild = 4;
formulas[13].val.children.rchild = 11;
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
if (resp->form == FORM_TRUE) { RingAddStep(resp->step, cStruct->ttime);}
else if (resp->form == FORM_FALSE) { RingAddStep(resp->step, cStruct->ftime);};
// increment
cres = (cres + 1) % theStruct[i].residues->size;
}
// could clean up extra stuff that's past time, but shouldn't ever really have any
}}
