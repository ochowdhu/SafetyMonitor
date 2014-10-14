/* bmtlTree.h -- keeping tree stuff in a separate header to keep the bison file cleaner
 * @author Aaron Kane
 *
 * */

#ifndef __BMTLTREE_H
#define __BMTLTREE_H

//#ifndef RESTRICT_LOGIC
//#define RESTRICT_LOGIC 0
//#endif

#include <set>
#include <vector>
#include <cstring>
#include "armUtils.h"

//enum nodeType {VALUE_T, PROP_T, NOT_T, OR_T, AND_T, IMPLIES_T, ALWAYS_T, EVENT_T, PALWAYS_T, PEVENT_T, UNTIL_T, SINCE_T };
bool RESTRICT_LOGIC = 1;
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
	tag formTag;
	std::vector<Node*> nList;
	std::vector<Node*> gList;
	int stidx;
} Node;

#define MAX(x,y) (((x) > (y)) ? (x) : (y))
// Global value nodes -- only want one copy of true/false
Node* trueNode;
Node* falseNode;
Node* invalNode;

int fdelay(Node* root) {
	switch (root->type) {
		case PROP_T:
		case VALUE_T:
			return 0;
		case NOT_T:
			return fdelay(root->val.child);
		case AND_T:
		case OR_T:
		case IMPLIES_T:
			return MAX(fdelay(root->val.binOp.lchild), fdelay(root->val.binOp.rchild));
		case UNTIL_T:
			return root->val.twotempOp.hbound + MAX(fdelay(root->val.twotempOp.lchild), fdelay(root->val.twotempOp.rchild));
		case SINCE_T:
			return MAX(fdelay(root->val.twotempOp.lchild), fdelay(root->val.twotempOp.rchild));
		default:
			return -1;
	}
}

int minbuflen(Node* root) {
	switch (root->type) {
		case PROP_T:
		case VALUE_T:
			return 0;
		case NOT_T:
			return minbuflen(root->val.child);
		case AND_T:
		case OR_T:
		case IMPLIES_T:
			return MAX(minbuflen(root->val.binOp.lchild), minbuflen(root->val.binOp.rchild));
		case UNTIL_T:
		case SINCE_T:
			return root->val.twotempOp.hbound + 1 + MAX(minbuflen(root->val.twotempOp.lchild), minbuflen(root->val.twotempOp.rchild));
		case ALWAYS_T:
		case EVENT_T:
		case PALWAYS_T:
		case PEVENT_T:
			return root->val.tempOp.hbound + 1 + minbuflen(root->val.tempOp.child);
		default:
			return -1;
	}
}

int stackDepth(Node* root) {
	switch (root->type) {
		case PROP_T:
		case VALUE_T:
			return 1;
		case NOT_T:
			return 1 + stackDepth(root->val.child);
		case AND_T:
		case OR_T:
		case IMPLIES_T:
			return 2 + MAX(stackDepth(root->val.binOp.lchild), stackDepth(root->val.binOp.rchild));
		case UNTIL_T:
		case SINCE_T:
			return 1;
		default:
			return -1;
	}
}

bool matchNodes(Node* n1, Node* n2) {
	if (n1->type == n2->type) {
		switch (n1->type) {
			case PROP_T:
				if (strcmp(n1->val.propName, n2->val.propName) == 0) {
					return true;  
				}
				return false;
			case VALUE_T:
				if (n1->val.value == n2->val.value) {
					return true;  
				}
				return false;
			case NOT_T:
				return matchNodes(n1->val.child, n2->val.child);
			case AND_T:
			case OR_T:
			case IMPLIES_T:
				return matchNodes(n1->val.binOp.lchild, n2->val.binOp.lchild) 
					   && matchNodes(n1->val.binOp.rchild, n2->val.binOp.rchild);
			case UNTIL_T:
			case SINCE_T:
				if (n1->val.twotempOp.lbound == n2->val.twotempOp.lbound 
					&& n1->val.twotempOp.hbound == n2->val.twotempOp.hbound) {
					//
					return matchNodes(n1->val.twotempOp.lchild, n2->val.twotempOp.lchild) 
					   && matchNodes(n1->val.twotempOp.rchild, n2->val.twotempOp.rchild);
				}
				return false;
			case EVENT_T:
			case ALWAYS_T:
			case PEVENT_T:
			case PALWAYS_T:
				if (n1->val.tempOp.lbound == n2->val.tempOp.lbound
					&& n1->val.tempOp.hbound == n2->val.tempOp.hbound) {
					//
					return matchNodes(n1->val.tempOp.child, n2->val.tempOp.child);
				}
				return false;
		}
	}
	return false;
}
void uniqueAdd(std::vector<Node*>* v, Node* n) {
	std::vector<Node*>::iterator it;
	bool found = false;
	for (it = v->begin(); it != v->end(); it++) {
		if ((*it)->type == n->type) {
			switch ((*it)->type) {
				case PROP_T:
					if (strcmp((*it)->val.propName, n->val.propName) == 0) {
						printf("UniqueAdd found a prop match with %s\n",n->val.propName);
						found = true;
					}
					break;
				case VALUE_T:
					if ((*it)->val.value == n->val.value) {
						found = true;
					}
					break;
				case NOT_T:
					//if ((*it)->val.child == n->val.child) {
					if (matchNodes(*it,n)) {
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
				case EVENT_T:
				case PEVENT_T:
				case ALWAYS_T:
				case PALWAYS_T:
					if ((*it)->val.tempOp.child == n->val.tempOp.child 
						&& (*it)->val.tempOp.lbound == n->val.tempOp.lbound 
						&& (*it)->val.tempOp.hbound == n->val.tempOp.hbound) {
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
				case EVENT_T:
				case PEVENT_T:
				case ALWAYS_T:
				case PALWAYS_T:
					if ((*it)->val.tempOp.child == n->val.tempOp.child 
						&& (*it)->val.tempOp.lbound == n->val.tempOp.lbound 
						&& (*it)->val.tempOp.hbound == n->val.tempOp.hbound) {
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
				case EVENT_T:
				case PEVENT_T:
				case ALWAYS_T:
				case PALWAYS_T:
					if ((*it)->val.tempOp.child == n->val.tempOp.child 
						&& (*it)->val.tempOp.lbound == n->val.tempOp.lbound 
						&& (*it)->val.tempOp.hbound == n->val.tempOp.hbound) {
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

Node *getValueNode(bool nval) {
	if (nval) {
		return trueNode;
	}
	return falseNode;
}
Node *makeValueNode(bool nval) {
	Node *n = new Node();
	n->type = VALUE_T;
	n->val.value = nval;
	n->nodeTag = tagCount++;
	n->stidx = -1;
	return n;
}

Node *makePropNode(char* name) {
	Node *n = new Node();
	n->type = PROP_T;
	n->val.propName = name;
	n->nodeTag = tagCount++;
	n->stidx = -1;
	return n;
}

Node *makeNotNode(Node* child) {
	Node *n = new Node();
	n->type = NOT_T;
	n->val.child = child;
	n->nodeTag = tagCount++;
	n->stidx = -1;
	return n;
}
Node *makeBinNode(enum nodeType type, Node* lchild, Node* rchild) {
	Node *n = new Node();
	n->type = type;
	n->val.binOp.lchild = lchild;
	n->val.binOp.rchild = rchild;
	n->nodeTag = tagCount++;
	n->stidx = -1;
	return n;
}
Node *makeImpNode(Node *lchild, Node *rchild) {
	if (RESTRICT_LOGIC) {
		return makeBinNode(OR_T, makeNotNode(lchild), rchild);
	} else {
		return makeBinNode(IMPLIES_T, lchild, rchild);
	}
}
Node *makeAndNode(Node *lchild, Node *rchild) {
	if (RESTRICT_LOGIC) {
		return makeNotNode(makeBinNode(OR_T, makeNotNode(lchild), makeNotNode(rchild)));
	} else {
		return makeBinNode(AND_T, lchild, rchild);
	}

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
	n->stidx = -1;
	return n;
}

Node *makeEventNode(int lbound, int hbound, Node* child) {
	if (RESTRICT_LOGIC) {
		return makeTwoTempNode(UNTIL_T, lbound, hbound, getValueNode(true), child);
	} else {
		return makeTempNode(EVENT_T, lbound, hbound, child);
	}
}
Node *makePEventNode(int lbound, int hbound, Node* child) {
	if (RESTRICT_LOGIC) {
		return makeTwoTempNode(SINCE_T, lbound, hbound, getValueNode(true), child);
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
