/** Auto Generated monitor configuration */
// FORMULA: ['orprop', ['prop', 'x0000'], ['notprop', ['orprop', ['prop', 'x0001'], ['notprop', ['impprop', ['prop', 'x0002'], ['prop', 'x0004']]]]]]
#include "monconfig.h"
const int ftype[NFORMULAS] = { VALUE_T, VALUE_T, VALUE_T, PROP_T, PROP_T, PROP_T, PROP_T, IMPLIES_T, NOT_T, NOT_T, NOT_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, NOT_T, NOT_T, NOT_T, NOT_T, NOT_T, NOT_T, NOT_T, NOT_T, NOT_T, NOT_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, OR_T, };
const formula notForms[NF_NOT] = {0,2,1,8,9,10,17,18,19,20,21,22,23,24,25,26,};
const formula orForms[NF_OR][NF_OR] = {{0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,1,2,4,5,8,6,9,7,10,3,17,11,18,19,12,20,13,21,22,14,23,15,24,25,16,26,},
{0,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,},
{0,4,2,0,11,12,13,14,15,16,27,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,5,2,11,0,0,0,0,0,0,29,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,8,2,12,0,0,0,0,0,0,30,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,6,2,13,0,0,0,0,0,0,36,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,9,2,14,0,0,0,0,0,0,37,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,7,2,15,0,0,0,0,0,0,43,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,10,2,16,0,0,0,0,0,0,44,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,3,2,27,29,30,36,37,43,44,0,28,31,32,33,34,35,38,39,40,41,42,45,46,47,48,49,},
{0,17,2,0,0,0,0,0,0,0,28,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,11,2,0,0,0,0,0,0,0,31,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,18,2,0,0,0,0,0,0,0,32,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,19,2,0,0,0,0,0,0,0,33,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,12,2,0,0,0,0,0,0,0,34,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,20,2,0,0,0,0,0,0,0,35,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,13,2,0,0,0,0,0,0,0,38,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,21,2,0,0,0,0,0,0,0,39,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,22,2,0,0,0,0,0,0,0,40,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,14,2,0,0,0,0,0,0,0,41,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,23,2,0,0,0,0,0,0,0,42,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,15,2,0,0,0,0,0,0,0,45,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,24,2,0,0,0,0,0,0,0,46,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,25,2,0,0,0,0,0,0,0,47,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,16,2,0,0,0,0,0,0,0,48,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
{0,26,2,0,0,0,0,0,0,0,49,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,},
};
const formula andForms[NF_AND][NF_AND] = {{0,0,0,},
{0,1,1,},
{0,1,2,},
};
const formula impForms[NF_IMP][NF_IMP] = {{0,0,0,0,0,},
{0,2,2,2,2,},
{0,1,2,5,6,},
{0,0,2,0,7,},
{0,0,2,0,0,},
};
const formula POLICIES[NPOLICIES] = { 49, };
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
}}

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
residue resbuffers[NSTRUCT][NBUFLEN];
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
formulas[3].orTag = 10;
formulas[3].andTag = -1;
formulas[3].impTag = -1;
formulas[4].type = PROP_T;
formulas[4].val.propMask = MASK_x0001;
formulas[4].notTag = 6;
formulas[4].orTag = 3;
formulas[4].andTag = -1;
formulas[4].impTag = -1;
formulas[5].type = PROP_T;
formulas[5].val.propMask = MASK_x0002;
formulas[5].notTag = 3;
formulas[5].orTag = 4;
formulas[5].andTag = -1;
formulas[5].impTag = 3;
formulas[6].type = PROP_T;
formulas[6].val.propMask = MASK_x0004;
formulas[6].notTag = 4;
formulas[6].orTag = 6;
formulas[6].andTag = -1;
formulas[6].impTag = 4;
formulas[7].type = IMPLIES_T;
formulas[7].val.children.lchild = 5;
formulas[7].val.children.rchild = 6;
formulas[7].notTag = 5;
formulas[7].orTag = 8;
formulas[7].andTag = -1;
formulas[7].impTag = -1;
formulas[8].type = NOT_T;
formulas[8].val.child = 5;
formulas[8].notTag = 8;
formulas[8].orTag = 5;
formulas[8].andTag = -1;
formulas[8].impTag = -1;
formulas[9].type = NOT_T;
formulas[9].val.child = 6;
formulas[9].notTag = 11;
formulas[9].orTag = 7;
formulas[9].andTag = -1;
formulas[9].impTag = -1;
formulas[10].type = NOT_T;
formulas[10].val.child = 7;
formulas[10].notTag = 14;
formulas[10].orTag = 9;
formulas[10].andTag = -1;
formulas[10].impTag = -1;
formulas[11].type = OR_T;
formulas[11].val.children.lchild = 4;
formulas[11].val.children.rchild = 5;
formulas[11].notTag = 7;
formulas[11].orTag = 12;
formulas[11].andTag = -1;
formulas[11].impTag = -1;
formulas[12].type = OR_T;
formulas[12].val.children.lchild = 4;
formulas[12].val.children.rchild = 8;
formulas[12].notTag = 9;
formulas[12].orTag = 15;
formulas[12].andTag = -1;
formulas[12].impTag = -1;
formulas[13].type = OR_T;
formulas[13].val.children.lchild = 4;
formulas[13].val.children.rchild = 6;
formulas[13].notTag = 10;
formulas[13].orTag = 17;
formulas[13].andTag = -1;
formulas[13].impTag = -1;
formulas[14].type = OR_T;
formulas[14].val.children.lchild = 4;
formulas[14].val.children.rchild = 9;
formulas[14].notTag = 12;
formulas[14].orTag = 20;
formulas[14].andTag = -1;
formulas[14].impTag = -1;
formulas[15].type = OR_T;
formulas[15].val.children.lchild = 4;
formulas[15].val.children.rchild = 7;
formulas[15].notTag = 13;
formulas[15].orTag = 22;
formulas[15].andTag = -1;
formulas[15].impTag = -1;
formulas[16].type = OR_T;
formulas[16].val.children.lchild = 4;
formulas[16].val.children.rchild = 10;
formulas[16].notTag = 15;
formulas[16].orTag = 25;
formulas[16].andTag = -1;
formulas[16].impTag = -1;
formulas[17].type = NOT_T;
formulas[17].val.child = 4;
formulas[17].notTag = -1;
formulas[17].orTag = 11;
formulas[17].andTag = -1;
formulas[17].impTag = -1;
formulas[18].type = NOT_T;
formulas[18].val.child = 11;
formulas[18].notTag = -1;
formulas[18].orTag = 13;
formulas[18].andTag = -1;
formulas[18].impTag = -1;
formulas[19].type = NOT_T;
formulas[19].val.child = 8;
formulas[19].notTag = -1;
formulas[19].orTag = 14;
formulas[19].andTag = -1;
formulas[19].impTag = -1;
formulas[20].type = NOT_T;
formulas[20].val.child = 12;
formulas[20].notTag = -1;
formulas[20].orTag = 16;
formulas[20].andTag = -1;
formulas[20].impTag = -1;
formulas[21].type = NOT_T;
formulas[21].val.child = 13;
formulas[21].notTag = -1;
formulas[21].orTag = 18;
formulas[21].andTag = -1;
formulas[21].impTag = -1;
formulas[22].type = NOT_T;
formulas[22].val.child = 9;
formulas[22].notTag = -1;
formulas[22].orTag = 19;
formulas[22].andTag = -1;
formulas[22].impTag = -1;
formulas[23].type = NOT_T;
formulas[23].val.child = 14;
formulas[23].notTag = -1;
formulas[23].orTag = 21;
formulas[23].andTag = -1;
formulas[23].impTag = -1;
formulas[24].type = NOT_T;
formulas[24].val.child = 15;
formulas[24].notTag = -1;
formulas[24].orTag = 23;
formulas[24].andTag = -1;
formulas[24].impTag = -1;
formulas[25].type = NOT_T;
formulas[25].val.child = 10;
formulas[25].notTag = -1;
formulas[25].orTag = 24;
formulas[25].andTag = -1;
formulas[25].impTag = -1;
formulas[26].type = NOT_T;
formulas[26].val.child = 16;
formulas[26].notTag = -1;
formulas[26].orTag = 26;
formulas[26].andTag = -1;
formulas[26].impTag = -1;
formulas[27].type = OR_T;
formulas[27].val.children.lchild = 3;
formulas[27].val.children.rchild = 4;
formulas[27].notTag = -1;
formulas[27].orTag = -1;
formulas[27].andTag = -1;
formulas[27].impTag = -1;
formulas[28].type = OR_T;
formulas[28].val.children.lchild = 3;
formulas[28].val.children.rchild = 17;
formulas[28].notTag = -1;
formulas[28].orTag = -1;
formulas[28].andTag = -1;
formulas[28].impTag = -1;
formulas[29].type = OR_T;
formulas[29].val.children.lchild = 3;
formulas[29].val.children.rchild = 5;
formulas[29].notTag = -1;
formulas[29].orTag = -1;
formulas[29].andTag = -1;
formulas[29].impTag = -1;
formulas[30].type = OR_T;
formulas[30].val.children.lchild = 3;
formulas[30].val.children.rchild = 8;
formulas[30].notTag = -1;
formulas[30].orTag = -1;
formulas[30].andTag = -1;
formulas[30].impTag = -1;
formulas[31].type = OR_T;
formulas[31].val.children.lchild = 3;
formulas[31].val.children.rchild = 11;
formulas[31].notTag = -1;
formulas[31].orTag = -1;
formulas[31].andTag = -1;
formulas[31].impTag = -1;
formulas[32].type = OR_T;
formulas[32].val.children.lchild = 3;
formulas[32].val.children.rchild = 18;
formulas[32].notTag = -1;
formulas[32].orTag = -1;
formulas[32].andTag = -1;
formulas[32].impTag = -1;
formulas[33].type = OR_T;
formulas[33].val.children.lchild = 3;
formulas[33].val.children.rchild = 19;
formulas[33].notTag = -1;
formulas[33].orTag = -1;
formulas[33].andTag = -1;
formulas[33].impTag = -1;
formulas[34].type = OR_T;
formulas[34].val.children.lchild = 3;
formulas[34].val.children.rchild = 12;
formulas[34].notTag = -1;
formulas[34].orTag = -1;
formulas[34].andTag = -1;
formulas[34].impTag = -1;
formulas[35].type = OR_T;
formulas[35].val.children.lchild = 3;
formulas[35].val.children.rchild = 20;
formulas[35].notTag = -1;
formulas[35].orTag = -1;
formulas[35].andTag = -1;
formulas[35].impTag = -1;
formulas[36].type = OR_T;
formulas[36].val.children.lchild = 3;
formulas[36].val.children.rchild = 6;
formulas[36].notTag = -1;
formulas[36].orTag = -1;
formulas[36].andTag = -1;
formulas[36].impTag = -1;
formulas[37].type = OR_T;
formulas[37].val.children.lchild = 3;
formulas[37].val.children.rchild = 9;
formulas[37].notTag = -1;
formulas[37].orTag = -1;
formulas[37].andTag = -1;
formulas[37].impTag = -1;
formulas[38].type = OR_T;
formulas[38].val.children.lchild = 3;
formulas[38].val.children.rchild = 13;
formulas[38].notTag = -1;
formulas[38].orTag = -1;
formulas[38].andTag = -1;
formulas[38].impTag = -1;
formulas[39].type = OR_T;
formulas[39].val.children.lchild = 3;
formulas[39].val.children.rchild = 21;
formulas[39].notTag = -1;
formulas[39].orTag = -1;
formulas[39].andTag = -1;
formulas[39].impTag = -1;
formulas[40].type = OR_T;
formulas[40].val.children.lchild = 3;
formulas[40].val.children.rchild = 22;
formulas[40].notTag = -1;
formulas[40].orTag = -1;
formulas[40].andTag = -1;
formulas[40].impTag = -1;
formulas[41].type = OR_T;
formulas[41].val.children.lchild = 3;
formulas[41].val.children.rchild = 14;
formulas[41].notTag = -1;
formulas[41].orTag = -1;
formulas[41].andTag = -1;
formulas[41].impTag = -1;
formulas[42].type = OR_T;
formulas[42].val.children.lchild = 3;
formulas[42].val.children.rchild = 23;
formulas[42].notTag = -1;
formulas[42].orTag = -1;
formulas[42].andTag = -1;
formulas[42].impTag = -1;
formulas[43].type = OR_T;
formulas[43].val.children.lchild = 3;
formulas[43].val.children.rchild = 7;
formulas[43].notTag = -1;
formulas[43].orTag = -1;
formulas[43].andTag = -1;
formulas[43].impTag = -1;
formulas[44].type = OR_T;
formulas[44].val.children.lchild = 3;
formulas[44].val.children.rchild = 10;
formulas[44].notTag = -1;
formulas[44].orTag = -1;
formulas[44].andTag = -1;
formulas[44].impTag = -1;
formulas[45].type = OR_T;
formulas[45].val.children.lchild = 3;
formulas[45].val.children.rchild = 15;
formulas[45].notTag = -1;
formulas[45].orTag = -1;
formulas[45].andTag = -1;
formulas[45].impTag = -1;
formulas[46].type = OR_T;
formulas[46].val.children.lchild = 3;
formulas[46].val.children.rchild = 24;
formulas[46].notTag = -1;
formulas[46].orTag = -1;
formulas[46].andTag = -1;
formulas[46].impTag = -1;
formulas[47].type = OR_T;
formulas[47].val.children.lchild = 3;
formulas[47].val.children.rchild = 25;
formulas[47].notTag = -1;
formulas[47].orTag = -1;
formulas[47].andTag = -1;
formulas[47].impTag = -1;
formulas[48].type = OR_T;
formulas[48].val.children.lchild = 3;
formulas[48].val.children.rchild = 16;
formulas[48].notTag = -1;
formulas[48].orTag = -1;
formulas[48].andTag = -1;
formulas[48].impTag = -1;
formulas[49].type = OR_T;
formulas[49].val.children.lchild = 3;
formulas[49].val.children.rchild = 26;
formulas[49].notTag = -1;
formulas[49].orTag = -1;
formulas[49].andTag = -1;
formulas[49].impTag = -1;
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
