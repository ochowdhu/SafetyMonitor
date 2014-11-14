/* monconfig.h --- putting monitor configuration stuff here
 * 
 * ideally we'll autogenerate this at some point, so putting all the 
 * variably configured stuff here
*/


#include "monitor.h"
#include "formula.h"
#include "gendefs.h"

#define NVALBUFS (NSTRUCT * 2)

// True/False
#define INVALID 2
#define TRUE 1
#define FALSE 0

// formula names
#define FORM_INVALID 0
#define FORM_FALSE 1
#define FORM_TRUE 2

// always going to use iterative reduce
#define ITERATIVE_RED

#define getProp(m) ((cstate[m/WORDSZ] & (1<<(m)))!=0)
extern volatile int cstate[NPROP/WORDSZ+(NPROP%WORDSZ!=0)], nstate[NPROP/WORDSZ+(NPROP%WORDSZ!=0)];

extern const int ftype[NFORMULAS];
extern const formula POLICIES[NPOLICIES];

// structure table
extern resStructure theStruct[NSTRUCT];
// formula table
extern fNode formulas[NFORMULAS];
// residue buffer table
extern resbuf rbuffers[NSTRUCT];
// interval buffer table
extern intNode intnodebuf[NSTRUCT][2][NBUFLEN];
extern intNode *intnodebufP[NSTRUCT][2][NBUFLEN];
extern intbuf intbuffer[NSTRUCT][2];
extern intring intringbuffer[NSTRUCT][2];
extern residue resbuffers[NSTRUCT][NBUFLEN];

// main list of residues
extern resbuf mainresbuf[NPOLICIES];
extern residue mainresbuffers[NPOLICIES][NBUFLEN];

// formula simplify lookup tables for reduce
extern const formula notForms[NF_NOT];
extern const formula orForms[NF_OR][NF_OR];
#ifdef FULL_LOGIC
extern const formula andForms[NF_AND][NF_AND];
extern const formula impForms[NF_IMP][NF_IMP];
#endif
//extern const formula untilForms[NFORMULAS][NFORMULAS];
//extern const formula sinceForms[NFORMULAS][NFORMULAS];

// iterative reduce stack stuff
extern formulaStack redStack;
extern formulaStack redStackVals;
extern formulaStack redStackDir;
extern formula redStackBuf[STACK_DEPTH];
extern formula redStackValsBuf[STACK_DEPTH];
extern formula redStackDirBuf[STACK_DEPTH];

extern void build_formula(void);
extern void build_struct(void);
extern void incrStruct(int step);

extern void traceViolate(int i);
extern void stepSatisfy(void);
extern void traceFail(void);
