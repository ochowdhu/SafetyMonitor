/* bmtlTree.h -- keeping tree stuff in a separate header to keep the bison file cleaner
 * @author Aaron Kane
 *
 * */

#ifndef __BMTLTREE_H
#define __BMTLTREE_H

#ifndef RESTRICT_LOGIC
#define RESTRICT_LOGIC 1
#endif

#include <set>
#include <vector>
#include <cstring>
#include "armUtils.h"

//enum nodeType {VALUE_T, PROP_T, NOT_T, OR_T, AND_T, IMPLIES_T, ALWAYS_T, EVENT_T, PALWAYS_T, PEVENT_T, UNTIL_T, SINCE_T };
tag tagCount = 0;
typedef struct Node {
	enum nodeType type;
	union {
		bool value;
		char* propName;			// for propositions
		struct Node* child; // for not
		struct {Node* lchild; struct Node* rchild;} binOp; // for and, or, implies
		struct {Node* child; int lbound; int hbound;} tempOp; // for temporal ops
		struct {Node* lchild; Node* rchild; int lbound; int hbound;} twotempOp; // for Since/Until temporal ops
	} val;
	std::set<confNode, confCompare> childList;
	std::set<confNode, confCompare> tempList;
	tag nodeTag;
	std::vector<Node*> nList;
	std::vector<Node*> gList;
} Node;

void uniqueAdd(std::vector<Node*>* v, Node* n) {
	std::vector<Node*>::iterator it;
	bool found = false;
	for (it = v->begin(); it != v->end(); it++) {
		if ((*it)->type == n->type) {
			switch ((*it)->type) {
				case PROP_T:
					if (strcmp((*it)->val.propName, n->val.propName) == 0) {
						found = true;
					}
					break;
				case VALUE_T:
					if ((*it)->val.value == n->val.value) {
						found = true;
					}
					break;
				case NOT_T:
					if ((*it)->val.child == n->val.child) {
						found = true;
					}
					break;
				case AND_T:
				case OR_T:
				case IMPLIES_T:
					if ((*it)->val.binOp.lchild == n->val.binOp.lchild && (*it)->val.binOp.rchild == n->val.binOp.rchild) {
						found = true;
					}
					break;
				case UNTIL_T:
				case SINCE_T:
					if ((*it)->val.twotempOp.lchild == n->val.twotempOp.lchild 
						&& (*it)->val.twotempOp.rchild == n->val.twotempOp.rchild 
						&& (*it)->val.twotempOp.lbound == n->val.twotempOp.lbound 
						&& (*it)->val.twotempOp.hbound == n->val.twotempOp.hbound) {
						found = true;
					}
					break;
			}
		} else {
			continue;
		}
	}
	if (!found) {
		(*v).push_back(n);
	}
}

void uniqueAdd(std::vector<Node*>* v, Node* n, std::vector<Node*>* v2) {
	std::vector<Node*>::iterator it;
	bool found = false;
	for (it = v->begin(); it != v->end(); it++) {
		if ((*it)->type == n->type) {
			switch ((*it)->type) {
				case PROP_T:
					if (strcmp((*it)->val.propName, n->val.propName) == 0) {
						found = true;
					}
					break;
				case VALUE_T:
					if ((*it)->val.value == n->val.value) {
						found = true;
					}
					break;
				case NOT_T:
					if ((*it)->val.child == n->val.child) {
						found = true;
					}
					break;
				case AND_T:
				case OR_T:
				case IMPLIES_T:
					if ((*it)->val.binOp.lchild == n->val.binOp.lchild && (*it)->val.binOp.rchild == n->val.binOp.rchild) {
						found = true;
					}
					break;
				case UNTIL_T:
				case SINCE_T:
					if ((*it)->val.twotempOp.lchild == n->val.twotempOp.lchild 
						&& (*it)->val.twotempOp.rchild == n->val.twotempOp.rchild 
						&& (*it)->val.twotempOp.lbound == n->val.twotempOp.lbound 
						&& (*it)->val.twotempOp.hbound == n->val.twotempOp.hbound) {
						found = true;
					}
					break;
			}
		} else {
			continue;
		}
	}

	for (it = v2->begin(); it != v2->end(); it++) {
		if ((*it)->type == n->type) {
			switch ((*it)->type) {
				case PROP_T:
					if (strcmp((*it)->val.propName, n->val.propName) == 0) {
						found = true;
					}
					break;
				case VALUE_T:
					if ((*it)->val.value == n->val.value) {
						found = true;
					}
					break;
				case NOT_T:
					if ((*it)->val.child == n->val.child) {
						found = true;
					}
					break;
				case AND_T:
				case OR_T:
				case IMPLIES_T:
					if ((*it)->val.binOp.lchild == n->val.binOp.lchild && (*it)->val.binOp.rchild == n->val.binOp.rchild) {
						found = true;
					}
					break;
				case UNTIL_T:
				case SINCE_T:
					if ((*it)->val.twotempOp.lchild == n->val.twotempOp.lchild 
						&& (*it)->val.twotempOp.rchild == n->val.twotempOp.rchild 
						&& (*it)->val.twotempOp.lbound == n->val.twotempOp.lbound 
						&& (*it)->val.twotempOp.hbound == n->val.twotempOp.hbound) {
						found = true;
					}
					break;
			}
		} else {
			continue;
		}
	}
	if (!found) {
		(*v).push_back(n);
	}
}

Node *copyNode(Node *n) {
	Node *n2 = new Node();
	n2->type = n->type;
	n2->val = n->val;
	n2->childList = std::set<confNode, confCompare>(n->childList);
	n2->tempList = std::set<confNode, confCompare>(n->tempList);
	return n2;
}
Node *makeValueNode(bool nval) {
	Node *n = new Node();
	n->type = VALUE_T;
	n->val.value = nval;
	n->nodeTag = tagCount++;
	return n;
}

Node *makePropNode(char* name) {
	Node *n = new Node();
	n->type = PROP_T;
	n->val.propName = name;
	n->nodeTag = tagCount++;
	return n;
}

Node *makeNotNode(Node* child) {
	Node *n = new Node();
	n->type = NOT_T;
	n->val.child = child;
	n->nodeTag = tagCount++;
	return n;
}
Node *makeBinNode(enum nodeType type, Node* lchild, Node* rchild) {
	Node *n = new Node();
	n->type = type;
	n->val.binOp.lchild = lchild;
	n->val.binOp.rchild = rchild;
	n->nodeTag = tagCount++;
	return n;
}
Node *makeTempNode(enum nodeType type, int lbound, int hbound, Node* child) {
	Node *n = new Node();
	n->type = type;
	n->val.tempOp.child = child;
	n->val.tempOp.lbound = lbound;
	n->val.tempOp.hbound = hbound;
	return n;
}
Node *makeTwoTempNode(enum nodeType type, int lbound, int hbound, Node* lchild, Node* rchild) {
	Node *n = new Node();
	n->type = type;
	n->val.twotempOp.lchild = lchild;
	n->val.twotempOp.rchild = rchild;
	n->val.twotempOp.lbound = lbound;
	n->val.twotempOp.hbound = hbound;
	n->nodeTag = tagCount++;
	return n;
}

Node *makeEventNode(int lbound, int hbound, Node* child) {
	if (RESTRICT_LOGIC) {
		return makeTwoTempNode(UNTIL_T, lbound, hbound, makeValueNode(true), child);
	} else {
		return makeTempNode(EVENT_T, lbound, hbound, child);
	}
}
Node *makePEventNode(int lbound, int hbound, Node* child) {
	if (RESTRICT_LOGIC) {
		return makeTwoTempNode(SINCE_T, lbound, hbound, makeValueNode(true), child);
	} else {
		return makeTempNode(PEVENT_T, lbound, hbound, child);
	}
}

Node *makeAlwaysNode(int lbound, int hbound, Node* child) {
	if (RESTRICT_LOGIC) {
		return makeNotNode(makeEventNode(lbound, hbound, makeNotNode(child)));
	} else {
		return makeTempNode(ALWAYS_T, lbound, hbound, child);
	}
}
Node *makePAlwaysNode(int lbound, int hbound, Node* child) {
	if (RESTRICT_LOGIC) {
		return makeNotNode(makePEventNode(lbound, hbound, makeNotNode(child)));
	} else {
		return makeTempNode(PALWAYS_T, lbound, hbound, child);
	}
}

#endif
