/* monconfig.h --- putting monitor configuration stuff here
 * 
 * ideally we'll autogenerate this at some point, so putting all the 
 * variably configured stuff here
*/


#include "monitor.h"
#include "formula.h"


#define NFORMULAS 8
#define NSTRUCT 2
#define NVALBUFS (NSTRUCT * 2)

// buffer len -- delay
#define NBUFLEN 40

// True/False
#define TRUE 1
#define FALSE 0

// prop masks
#define MASK_A 0x01
#define MASK_B 0x02
#define MASK_C 0x04

// formula names
#define FORM_A 0
#define FORM_B 1
#define FORM_C 2
#define FORM_BUC 3
#define FORM_NA 4
#define FORM_NAOBUC 5
#define FORM_TRUE	6
#define FORM_FALSE 7

#define FORM_DELAY 40

extern const int ftype[NFORMULAS];

// structure table
extern resStructure theStruct[NSTRUCT];
// formula table
extern fNode formulas[NFORMULAS];
// residue buffer table
extern resbuf rbuffers[NSTRUCT];
// interval buffer table
extern interval ibuffers[NSTRUCT][NBUFLEN*2];
extern residue resbuffers[NSTRUCT][NBUFLEN];

// formula simplify lookup tables for reduce
extern const formula notForms[NFORMULAS];
extern const formula orForms[NFORMULAS][NFORMULAS];
extern const formula untilForms[NFORMULAS][NFORMULAS];
extern const formula sinceForms[NFORMULAS][NFORMULAS];

extern void build_formula(void);
extern void build_struct(void);
extern void incrStruct(int step);


