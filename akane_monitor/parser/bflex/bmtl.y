%{

#include <iostream>
#include <cstdio>

// flex stuff
extern "C" int yylex();
extern "C" int yyparse();
extern "C" FILE *yyin;

void yyerror(const char* s);


enum nodeType {PROP_T, NOT_T, OR_T, AND_T, IMPLIES_T, ALWAYS_T, EVENT_T, PALWAYS_T, PEVENT_T, UNTIL_T, SINCE_T };
typedef struct Node {
	enum nodeType type;
	union {
		char* propName;			// for propositions
		struct Node* child; // for not
		struct {Node* lchild; struct Node* rchild;} binOp; // for and, or, implies
		struct {Node* child; int lbound; int hbound;} tempOp; // for temporal ops
		struct {Node* lchild; Node* rchild; int lbound; int hbound;} twotempOp; // for Since/Until temporal ops
	} val;
} Node;

Node *ast;
Node *makePropNode(char* name) {
	Node *n = new Node();
	n->type = PROP_T;
	n->val.propName = name;
	return n;
}

Node *makeNotNode(Node* child) {
	Node *n = new Node();
	n->type = PROP_T;
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

void pprintTree(Node *n);
void lispPrint(Node *n);
%}

%union {
	int ival;
	char* sval;
	struct Node* nval;
}


%token <ival> BOUND
%token NOT AND OR IMPLIES
%token EVENT_L PEVENT_L ALWAYS_L PALWAYS_L
%token EVENT_R PEVENT_R ALWAYS_R PALWAYS_R
%token UNTIL SINCE
%token BSEP ENDL PAREN
%token <sval> PROP

%type<nval> expression
%nonassoc '(' ')'
%left NOT 
%left AND OR IMPLIES
%nonassoc ',' BOUND ALWAYS_L ALWAYS_R EVENT_L EVENT_R
%nonassoc PALWAYS_L PALWAYS_R PEVENT_L PEVENT_R
%nonassoc UNTIL SINCE

%% 
formula:
	expression ENDL { ast = $1; std::cout << "got expression" << std::endl;} 
	;

expression:
	 PROP { $$ = makePropNode($1); } // std::cout << "bison got prop: " << $1 << std::endl; }
	| '(' expression ')' {$$ = $2; } // std::cout << "parenthesized expression -- keep going" <<  std::endl; }
	|  NOT expression { $$ = makeNotNode($2); } //  std::cout << "bison got not" << std::endl; }
	| expression AND expression { $$ = makeBinNode(AND_T, $1, $3); } // std::cout << "bison got and" << std::endl; }
	| expression OR expression { $$ = makeBinNode(OR_T, $1, $3); } //std::cout << "bison got or" << std::endl; }
	| expression IMPLIES expression { $$ = makeBinNode(IMPLIES_T, $1, $3); } // std::cout << "bison got implies" << std::endl; }
	| ALWAYS_L BOUND ',' BOUND ALWAYS_R expression	{ $$ = makeTempNode(ALWAYS_T, $2, $4, $6); } // std::cout << "bison got always" << std::endl; }
	| EVENT_L BOUND ',' BOUND EVENT_R expression	{ $$ = makeTempNode(EVENT_T, $2, $4, $6); } // std::cout << "bison got eventually" << std::endl; }
	| PALWAYS_L BOUND ',' BOUND PALWAYS_R expression	{ $$ = makeTempNode(PALWAYS_T, $2, $4, $6); } // std::cout << "bison got past_always" << std::endl; }
	| PEVENT_L BOUND ',' BOUND PEVENT_R expression	{ $$ = makeTempNode(PEVENT_T, $2, $4, $6); } //std::cout << "bison got past eventually" << std::endl; }
	| expression UNTIL BOUND ',' BOUND UNTIL expression { $$ = makeTwoTempNode(UNTIL_T, $3, $5, $1, $7); } //std::cout << "bison got until" << std::endl;}
	| expression SINCE BOUND ',' BOUND SINCE expression { $$ = makeTwoTempNode(SINCE_T, $3, $5, $1, $7); } //std::cout << "bison got since" << std::endl;}
	;
%%

main(int argc, char** argv) {
	FILE *myfile;
	if (argc > 1) {
		yyin = fopen(argv[1], "r");
		//yyin = myfile;
	}

	do {
		yyparse();
	} while (!feof(yyin));
	std::cout << "ok, let's check this tree..." << std::endl;
	if (ast) {
		//pprintTree(ast);
		std::cout << "Trying lisp print" << std::endl;
		lispPrint(ast);
		std::cout << std::endl;
	}
}

void pprintTree(Node* root) {
	switch (root->type) {
		case PROP_T:
			std::cout << "Prop Node: " << root->val.propName << std::endl;
			break;
		case NOT_T:
			std::cout << "Not Node: " << std::endl << "Child is..." << std::endl;
			pprintTree(root->val.child);
			break;
		case OR_T:
		case AND_T:
		case IMPLIES_T:
			std::cout << "Bin node, type: " << root->type << " and children:" << std::endl;
			std::cout << "lchild:";
			pprintTree(root->val.binOp.lchild);
			std::cout << "rchild:";
			pprintTree(root->val.binOp.rchild);
			break;
		case ALWAYS_T:
		case EVENT_T:
		case PALWAYS_T:
		case PEVENT_T:
			std::cout << "Temporal Bin node, type: " << root->type << ", bounds: [" << root->val.tempOp.lbound << ", " << root->val.tempOp.hbound << "] and children:" << std::endl;
			std::cout << "child:";
			pprintTree(root->val.tempOp.child);
			break;
		case SINCE_T:
		case UNTIL_T:
			std::cout << "Since/Until Bin node, type: " << root->type << ", bounds: [" << root->val.twotempOp.lbound << ", " << root->val.twotempOp.hbound << "] and children:" << std::endl;
			std::cout << "lchild:";
			pprintTree(root->val.twotempOp.lchild);
			std::cout << "rchild:";
			pprintTree(root->val.twotempOp.rchild);
			break;
	}
}

void lispPrint(Node* root) {
	switch (root->type) {
		case PROP_T:
			std::cout << "['prop', '" << root->val.propName << "']";
			break;
		case NOT_T:
			std::cout << "['not', ";
			lispPrint(root->val.child);
			std::cout << "]";
			break;
		case AND_T:
			std::cout << "['andprop', ";
			lispPrint(root->val.binOp.lchild);
			std::cout << ", ";
			lispPrint(root->val.binOp.rchild);
			std::cout << "]";
			break;
		case OR_T:
			std::cout << "['orprop', ";
			lispPrint(root->val.binOp.lchild);
			std::cout << ", ";
			lispPrint(root->val.binOp.rchild);
			std::cout << "]";
			break;
		case IMPLIES_T:
			std::cout << "['impprop', ";
			lispPrint(root->val.binOp.lchild);
			std::cout << ", ";
			lispPrint(root->val.binOp.rchild);
			std::cout << "]";
			break;
		case ALWAYS_T:
			std::cout << "['alwaysprop', " << root->val.tempOp.lbound << ", " << root->val.tempOp.hbound << ", ";
			lispPrint(root->val.tempOp.child);
			std::cout << "]";
			break;
		case EVENT_T:
			std::cout << "['eventprop', " << root->val.tempOp.lbound << ", " << root->val.tempOp.hbound << ", ";
			lispPrint(root->val.tempOp.child);
			std::cout << "]";
			break;
		case PALWAYS_T:
			std::cout << "['palwaysprop', " << root->val.tempOp.lbound << ", " << root->val.tempOp.hbound << ", ";
			lispPrint(root->val.tempOp.child);
			std::cout << "]";
			break;
		case PEVENT_T:
			std::cout << "['peventprop', " << root->val.tempOp.lbound << ", " << root->val.tempOp.hbound << ", ";
			lispPrint(root->val.tempOp.child);
			std::cout << "]";
			break;
		case SINCE_T:
			std::cout << "['sinceprop', " << root->val.twotempOp.lbound << ", " << root->val.twotempOp.hbound << ", ";
			lispPrint(root->val.twotempOp.lchild);
			std::cout << ", ";
			lispPrint(root->val.twotempOp.rchild);
			std::cout << "]";
			break;
		case UNTIL_T:
			std::cout << "['untilprop', " << root->val.twotempOp.lbound << ", " << root->val.twotempOp.hbound << ", ";
			lispPrint(root->val.twotempOp.lchild);
			std::cout << ", ";
			lispPrint(root->val.twotempOp.rchild);
			std::cout << "]";
			break;
		default:
			std::cout << "ERROR!";
			break;
	}
}
void yyerror(const char *s) {
	std::cout << "!! Parser error! Message " << s << std::endl;
	exit(-1);
}
