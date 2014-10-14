/* formula.h -- keep formula stuff here */

#ifndef __FORMULA_H
#define __FORMULA_H

/*
typedef struct formula {
	char type;
} formula;
*/
// formula's are uniquely id'ed by their table offset
typedef char formula;

//#ifdef FULL_LOGIC
enum nodeType {VALUE_T, PROP_T, NOT_T, OR_T, AND_T, IMPLIES_T, UNTIL_T, SINCE_T, EVENT_T, ALWAYS_T, PEVENT_T, PALWAYS_T};
//#else
//enum nodeType {VALUE_T, PROP_T, NOT_T, OR_T, UNTIL_T, SINCE_T};
//#endif

typedef struct fNode {
	enum nodeType type;
	formula theFormula;
	int structidx;
	union {
		char value;		// for true/false
		int propMask;	// for proposition
		formula child;	// for NOT
		struct {formula lchild; formula rchild;} children;	// for OR
		struct {formula lchild; formula rchild; int lbound; int hbound;} t_children; // for until/since
	} val;
} fNode;

/*
typedef struct fNode {
	enum nodeType type;
	formula theFormula;
	int structidx;
	union {
		char value;		// for true/false
		int propMask;	// for proposition
		struct fNode* child;	// for NOT
		struct {struct fNode* lchild; struct fNode* rchild;} children;	// for OR
		struct {struct fNode* lchild; struct fNode* rchild; int lbound; int hbound;} t_children; // for until/since
	} val;
} fNode;
*/
#endif
