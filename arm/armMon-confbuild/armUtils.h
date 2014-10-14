/* armUtils.h -- stuff to build arm config */


#ifndef __ARMUTILS_H
#define __ARMUTILS_H

//#include "bmtlTree.h"
#include <string>

#define NONE -1
enum nodeType {VALUE_T, PROP_T, NOT_T, OR_T, AND_T, IMPLIES_T, ALWAYS_T, EVENT_T, PALWAYS_T, PEVENT_T, UNTIL_T, SINCE_T };
static const std::string typeStrings[] = {"VALUE_T", "PROP_T", "NOT_T", "OR_T", "AND_T", "IMPLIES_T", "ALWAYS_T", "EVENT_T", "PALWAYS_T", "PEVENT_T", "UNTIL_T", "SINCE_T"};
typedef int tag;

struct confNode {
	enum nodeType type;
	std::string pname;
	tag nodetag;
	tag lchild;
	tag rchild;
};

struct confCompare {
	bool operator() (const confNode &lhs, const confNode &rhs) {
		return lhs.nodetag < rhs.nodetag;
	}
};

#endif
