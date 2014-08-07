/* bmtlTree.h -- keeping tree stuff in a separate header to keep the bison file cleaner
 * @author Aaron Kane
 *
 * */

#ifndef RESTRICT_LOGIC
#define RESTRICT_LOGIC 1
#endif

enum nodeType {VALUE_T, PROP_T, NOT_T, OR_T, AND_T, IMPLIES_T, ALWAYS_T, EVENT_T, PALWAYS_T, PEVENT_T, UNTIL_T, SINCE_T };
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
} Node;

Node *makeValueNode(bool nval) {
	Node *n = new Node();
	n->type = VALUE_T;
	n->val.value = nval;
	return n;
}

Node *makePropNode(char* name) {
	Node *n = new Node();
	n->type = PROP_T;
	n->val.propName = name;
	return n;
}

Node *makeNotNode(Node* child) {
	Node *n = new Node();
	n->type = NOT_T;
	n->val.child = child;
	return n;
}
Node *makeBinNode(enum nodeType type, Node* lchild, Node* rchild) {
	Node *n = new Node();
	n->type = type;
	n->val.binOp.lchild = lchild;
	n->val.binOp.rchild = rchild;
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
