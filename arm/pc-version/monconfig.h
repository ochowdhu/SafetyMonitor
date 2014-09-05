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


extern const int ftype[NFORMULAS];

///a -> b U_0,1s c

// structure table
extern resStructure theStruct[NSTRUCT];
// formula table
extern fNode formulas[NFORMULAS];
// residue buffer table
extern resbuf rbuffers[NSTRUCT];
// interval buffer table
extern interval ibuffers[NSTRUCT][NBUFLEN*2];
extern residue resbuffers[NSTRUCT][NBUFLEN];

// main list of residues
extern resbuf mainresbuf;
extern residue mainresbuffers[NBUFLEN];

// formula simplify lookup tables for reduce
extern const formula notForms[NFORMULAS];
extern const formula orForms[NFORMULAS][NFORMULAS];
extern const formula untilForms[NFORMULAS][NFORMULAS];
extern const formula sinceForms[NFORMULAS][NFORMULAS];

extern void build_formula(void);
extern void build_struct(void);
extern void incrStruct(int step);

