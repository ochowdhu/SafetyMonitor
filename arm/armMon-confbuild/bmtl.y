%{

#include <iostream>
#include <cstdio>
#include "bmtlTree.h"
#include <map>
#include <algorithm>

// flex stuff
extern "C" int yylex();
extern "C" int yyparse();
extern "C" FILE *yyin;

void yyerror(const char* s);

std::map<tag, Node*> nodeMap;
Node* ast;
tag GTAG;
void pprintTree(Node *n);
void lispPrint(Node *n);
void tagAndBuild(Node *n);
void tagAndBuild2(Node *n);
bool sortNList(Node* lhs, Node* rhs);
void confFormPrint(std::vector<Node*> forms, std::ostream &os); 
void confPrintMasks(std::vector<Node*> forms, std::ostream &os); 
void confBuildStruct(std::vector<Node*> forms, std::ostream &os);
void confBuildSimpTables(int nform, std::vector<Node*> list, std::ostream &os);
%}

%union {
	bool bval;
	int ival;
	char* sval;
	struct Node* nval;
}


%token <bval> VALUE
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
	VALUE { $$ = getValueNode($1); } //std::cout << " bison got val: " << $1 << std::endl; }
	| PROP { $$ = makePropNode($1); } // std::cout << "bison got prop: " << $1 << std::endl; }
	| '(' expression ')' {$$ = $2; } // std::cout << "parenthesized expression -- keep going" <<  std::endl; }
	| NOT expression { $$ = makeNotNode($2); } //  std::cout << "bison got not" << std::endl; }
	| expression AND expression { $$ = makeNotNode(makeBinNode(OR_T, makeNotNode($1), makeNotNode($3))); } // std::cout << "bison got and" << std::endl; }
	| expression OR expression { $$ = makeBinNode(OR_T, $1, $3); } //std::cout << "bison got or" << std::endl; }
	| expression IMPLIES expression { $$ = makeBinNode(OR_T, makeNotNode($1), $3); } // std::cout << "bison got implies" << std::endl; }
	| ALWAYS_L BOUND ',' BOUND ALWAYS_R expression	{ $$ = makeAlwaysNode($2, $4, $6); } // std::cout << "bison got always" << std::endl; }
	| EVENT_L BOUND ',' BOUND EVENT_R expression	{ $$ = makeEventNode($2, $4, $6); } // std::cout << "bison got eventually" << std::endl; }
	| PALWAYS_L BOUND ',' BOUND PALWAYS_R expression	{ $$ = makePAlwaysNode($2, $4, $6); } // std::cout << "bison got past_always" << std::endl; }
	| PEVENT_L BOUND ',' BOUND PEVENT_R expression	{ $$ = makePEventNode($2, $4, $6); } //std::cout << "bison got past eventually" << std::endl; }
	| expression UNTIL BOUND ',' BOUND UNTIL expression { $$ = makeTwoTempNode(UNTIL_T, $3, $5, $1, $7); } //std::cout << "bison got until" << std::endl;}
	| expression SINCE BOUND ',' BOUND SINCE expression { $$ = makeTwoTempNode(SINCE_T, $3, $5, $1, $7); } //std::cout << "bison got since" << std::endl;}
	;

%%


/*** What we need to do:
		generate simplify tables:
			loop over formulas, fill in each formulas entry in the table
			i.e. a || b --> simpOr[a][b], ~a -> simpNot[a], ~True -> simpNot[F]
			remember to fill in T/F columns correctly for everything
		generate build_formula():
			build a formula for each formula -- use correct structidx -- build these bottom up
		generate build_struct():
			order formulas, print initResStruct() for each struct formula in order based on structidx above

		Order of stuff:
			parse formula into AST
			build total formula list and global list and sort these lists

			generate build_struct -- DFS or sorted walk create initResStruct calls and assign struxtidx
			generate build_formula -- DFS or sorted walk create build_formula calls
			generate simplify tables -- loop over all formulas, fill in tables

*/

struct findNode {
	Node* node;
	findNode(Node* node) : node(node) {}
	bool operator()(Node *n) { 
		std::cout << "matching " << node->nodeTag << " against " << n->nodeTag << std::endl;
		return matchNodes(node, n);
	}
};

int main(int argc, char** argv) {
	GTAG = 0;
	FILE *myfile;
	// create value nodes
	invalNode = makeValueNode(2);
	trueNode = makeValueNode(1);
	falseNode = makeValueNode(0);
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
		std::cout << "Using formula" << std::endl;
		lispPrint(ast);
		std::cout << std::endl;
		std::cout << "trying tag&build" << std::endl;
		tagCount = 3;
		tagAndBuild2(ast);
		std::cout << "sorting tagged list..." << std::endl;
		std::sort(ast->nList.begin(), ast->nList.end(), sortNList);
		std::sort(ast->gList.begin(), ast->gList.end(), sortNList);

		std::vector<Node*>::iterator it;
		/*
		std::cout << "tagged, top list?" << std::endl;
		std::vector<Node*>::iterator it;
		int count = 0;
		for (it = ast->nList.begin(); it != ast->nList.end(); it++) {
			std::cout << count++ << "@" << (*it)->nodeTag << "|Node: ";  
			lispPrint(*it);
			std::cout << std::endl;
		}
		std::cout << "and, global list?" << std::endl;
		count = 0;
		for (it = ast->gList.begin(); it != ast->gList.end(); it++) {
			std::cout << count++ << "@" << (*it)->nodeTag << "|gNode: ";  
			lispPrint(*it);
			std::cout << std::endl;
		}
		*/
		std::vector<Node*> all(ast->nList);
		all.insert(all.end(), ast->gList.begin(), ast->gList.end());

		std::cout << "joined list:" << std::endl;
		std::sort(all.begin(), all.end(), sortNList);
		for (it = all.begin(); it != all.end(); it++) {
			std::cout << (*it)->nodeTag << "|gNode: ";
			lispPrint(*it);
			std::cout << std::endl;

		}
		std::cout << "JOINED LIST CONFIG PRINT: " << std::endl;
		std::cout << "NFORMULAS: " << all.size()+2 <<  std::endl;
		std::cout << "NSTRUCT: " << ast->gList.size() << std::endl;


///////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////
		std::cout << "AUTO-GENERATE CONFIG:" << std::endl;
		// First, into gendefs.h we need NFORMULAS, NSTRUCT, NBUFLEN, FORMDELAY
		std::cout << "/** Auto Generated definitions */" << std::endl
				  << "#define NFORMULAS (" << all.size()+2 << ")" << std::endl
				  << "#define NSTRUCT (" << ast->gList.size() << ")" << std::endl
				  << "#define NBUFLEN (" << 0 << ")" << std::endl
				  << "#define FORM_DELAY (" << 0 << ")" << std::endl;
		// throw masks into gendefs for now
		confPrintMasks(all, std::cout);
		// Now, monconfig.c
		std::cout << "/** Auto Generated monitor configuration */" << std::endl;
		std::cout << "#include \"monconfig.h\"" << std::endl;
		confBuildSimpTables(all.size()+2, all, std::cout);
		// fill in definitions
		std::cout << "// structure table" << std::endl 
				  << "resStructure theStruct[NSTRUCT];" << std::endl
				  << "// formula table" << std::endl
				  << "fNode formulas[NFORMULAS];" << std::endl
				  << "// buffer table" << std::endl
				  << "resbuf rbuffers[NSTRUCT];" << std::endl
				  << "interval ibuffers[NSTRUCT][NBUFLEN*2];" << std::endl
				  << "residue resbuffers[NSTRUCT][NBUFLEN];" << std::endl
				  << "// main list of residues" << std::endl
				  << "resbuf mainresbuf;" << std::endl 
				  << "residue mainresbuffers[NBUFLEN];" << std::endl;

		// print formulas
		std::cout << "// build formulas" << std::endl << "void build_formula(void) {" << std::endl;
		confFormPrint(all, std::cout);
		std::cout << "}" << std::endl << std::endl;

		// print structures
		std::cout << "// build structures" << std::endl << "void build_struct(void) {" << std::endl;
		//@TODO should put actual delay per structure in here eventually
		std::cout << "int i;" << std::endl
				  << "resbInit(&mainresbuf, NBUFLEN, mainresbuffers);" << std::endl
				  << "for (i = 0; i < NSTRUCT; i++) { rbuffers[i].size = NBUFLEN; rbuffers[i].buf = resbuffers[i]; }";
		confBuildStruct(ast->gList, std::cout);
		std::cout <<"}" << std::endl << std::endl;

		// and lastly dump incr_struct here
		std::cout << "void incrStruct(int step) { " << std::endl
				  << "// loop over struct (make sure struct is built smallest to largest...) " << std::endl
				  << "int i, cres, eres;" << std::endl
				  << "for (i = 0; i < NSTRUCT; i++) {" << std::endl
				  << "resStructure *cStruct = &theStruct[i];" << std::endl
				  << "// add residue to structure" << std::endl 
				  << "rbInsert(cStruct->residues, step, cStruct->formula);" << std::endl
				  << "// call reduce on all residues" << std::endl
				  << "cres = cStruct->residues->start;" << std::endl
				  << "eres = cStruct->residues->end;" << std::endl
				  << "// loop over every residue" << std::endl
				  << "while (cres != eres) {" << std::endl
				  << "reduce(stGetRes(cStruct, cres));" << std::endl
				  << "// increment" << std::endl
				  << "cres = (cres + 1) % theStruct[i].residues->size;" << std::endl
				  << "}" << std::endl
				  << "// could clean up extra stuff that's past time, but shouldn't ever really have any" << std::endl
				  << "}}" << std::endl;
																																									
		}


		std::cout << "DONE!!!!!!!!!!!!" << std::endl;


	}

bool sortNList(Node* lhs, Node*rhs) {
	return (lhs->nodeTag < rhs->nodeTag);
}

void tagAndBuild2(Node* root) {
	std::vector<Node *>::iterator itl, itr;
	Node* np;
	Node* np2;
	switch (root->type) {
		case VALUE_T:
			break;
		case PROP_T:
			root->nodeTag = GTAG++;
			//uniqueAdd(&root->nList, makePropNode(root->val.propName), &root->gList);
			uniqueAdd(&root->nList, makePropNode(root->val.propName));
			break;
		case NOT_T:
			// build children
			tagAndBuild2(root->val.child);
			// copy child list
			root->nList.insert(root->nList.end(), root->val.child->nList.begin(), root->val.child->nList.end());
			// copy global (hidden temporal) list
			root->gList.insert(root->gList.end(), root->val.child->gList.begin(), root->val.child->gList.end());
			/*for (itr = root->val.child->gList.begin(); itr != root->val.child->gList.end(); irt++) {
				uniqueAdd(&root->gList, *itr, &root->nList);
			}*/
			// add all possible children to childList
			for (itl = root->val.child->nList.begin(); itl != root->val.child->nList.end(); itl++) {
				//uniqueAdd(&root->nList, *itl);
				uniqueAdd(&root->nList, makeNotNode(*itl));
			}
			break;
		case OR_T:
		case AND_T:
		case IMPLIES_T:
			// build children
			tagAndBuild2(root->val.binOp.lchild);
			tagAndBuild2(root->val.binOp.rchild);
			// copy children lists
			root->nList.insert(root->nList.end(), root->val.binOp.lchild->nList.begin(), root->val.binOp.lchild->nList.end());
			root->nList.insert(root->nList.end(), root->val.binOp.rchild->nList.begin(), root->val.binOp.rchild->nList.end());
			// copy global (hidden temporal) list
			root->gList.insert(root->gList.end(), root->val.binOp.lchild->gList.begin(), root->val.binOp.lchild->gList.end());
			root->gList.insert(root->gList.end(), root->val.binOp.rchild->gList.begin(), root->val.binOp.rchild->gList.end());
			// add all possible children
			for (itl = root->val.binOp.lchild->nList.begin(); itl != root->val.binOp.lchild->nList.end(); itl++) {
				for (itr = root->val.binOp.rchild->nList.begin(); itr != root->val.binOp.rchild->nList.end(); itr++) {
					//uniqueAdd(&root->nList, *itl, &root->gList);
					//uniqueAdd(&root->nList, *itr, &root->gList);
					uniqueAdd(&root->nList, makeBinNode(root->type, *itl, *itr), &root->gList);
				}
			}
			break;
		case ALWAYS_T:
		case EVENT_T:
		case PALWAYS_T:
		case PEVENT_T:
			break;
		case SINCE_T:
		case UNTIL_T:
			// build children
			tagAndBuild2(root->val.twotempOp.lchild);
			tagAndBuild2(root->val.twotempOp.rchild);
			// copy children lists to global list
			root->gList.insert(root->gList.end(), root->val.twotempOp.lchild->nList.begin(), root->val.twotempOp.lchild->nList.end());
			root->gList.insert(root->gList.end(), root->val.twotempOp.rchild->nList.begin(), root->val.twotempOp.rchild->nList.end());
			// add all possible children -- just ourself
			if (root->val.twotempOp.lchild->type == VALUE_T) {
				np = getValueNode(root->val.twotempOp.lchild->val.value);
			} else {
				itl = find_if(root->gList.begin(), root->gList.end(), findNode(root->val.twotempOp.lchild));
				np = *itl;
			}

			if (root->val.twotempOp.rchild->type == VALUE_T) {
				np2 = getValueNode(root->val.twotempOp.rchild->val.value);
			} else {
				itr = find_if(root->gList.begin(), root->gList.end(), findNode(root->val.twotempOp.rchild));
				np2 = *itr;
			}
			//uniqueAdd(&root->nList, makeTwoTempNode(root->type, root->val.twotempOp.lbound, root->val.twotempOp.hbound, root->val.twotempOp.lchild, root->val.twotempOp.rchild), &root->gList);
			uniqueAdd(&root->nList, makeTwoTempNode(root->type, root->val.twotempOp.lbound, root->val.twotempOp.hbound, np, np2), &root->gList);
			break;
	}
}

void tagAndBuild(Node* root) {
	confNode c;
	switch (root->type) {
		case VALUE_T:
			break;
		case PROP_T:
			// add confNode to list
			c.type = PROP_T;
			c.pname = root->val.propName;
			c.nodetag = GTAG;
			c.lchild = NONE;
			c.rchild = NONE;
			// add confNode to child list
			root->childList.insert(c);
			nodeMap[GTAG++] = copyNode(root);
			break;
		case NOT_T:
			// build children
			tagAndBuild(root->val.child);
			// add self to nodeMap
			nodeMap[GTAG++] = copyNode(root);
			// add all possible children to childList
			root->childList.insert(root->val.child->childList.begin(),root->val.child->childList.end());
			for (std::set<confNode,confCompare>::iterator n = root->childList.begin(); n != root->childList.end(); n++) {
				c.type = NOT_T;
				c.pname = "";
				c.nodetag = GTAG++;
				c.lchild = n->nodetag;
				c.rchild = NONE;
				root->childList.insert(c);
			}
			break;
		case OR_T:
		case AND_T:
		case IMPLIES_T:
			tagAndBuild(root->val.binOp.lchild);
			tagAndBuild(root->val.binOp.rchild);
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
void pprintTree(Node* root) {
	switch (root->type) {
		case VALUE_T:
			std::cout << "Value Node: " << root->val.value << std::endl;
			break;
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
		case VALUE_T:
			std::cout << root->val.value;
			break;
		case PROP_T:
			std::cout << "['prop', '" << root->val.propName << "']";
			break;
		case NOT_T:
			std::cout << "['notprop', ";
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

void confPrintMasks(std::vector<Node*> forms, std::ostream &os) {
	int index = 0;
	std::vector<Node*>::iterator it;
	for (it = forms.begin(); it != forms.end(); it++) {
		if ((*it)->type == PROP_T) { 
			os << "#define MASK_" << (*it)->val.propName << " (1<<(" << index << "))" << std::endl;
			index++;
		}
	}
}

void confFormPrint(std::vector<Node*> forms, std::ostream &os) {
	int index = 3;
	std::vector<Node*>::iterator it;
	// INVALID/TRUE/FALSE come from template...
	os << "formulas[0].type = VALUE_T;" << std::endl << "formulas[0].val.value = INVALID;" << std::endl;
	os << "formulas[1].type = VALUE_T;" << std::endl << "formulas[1].val.value = FALSE;" << std::endl;
	os << "formulas[2].type = VALUE_T;" << std::endl << "formulas[2].val.value = TRUE;" << std::endl;
	for (it = forms.begin(); it != forms.end(); it++) {
		switch ((*it)->type) {
			case VALUE_T:
				os << "formulas[" << index << "].type = VALUE_T;" << std::endl;
				os << "formulas[" << index << "].val.value = " << (*it)->val.value << ";" << std::endl;
				index++;
				break;
			case PROP_T:
				os << "formulas[" << index << "].type = PROP_T;" << std::endl;
				os << "formulas[" << index << "].val.propMask = MASK_" << (*it)->val.propName << ";" << std::endl;
				index++;
				break;
			case NOT_T:
				os << "formulas[" << index << "].type = NOT_T;" << std::endl;
				os << "formulas[" << index << "].val.child = " << (*it)->val.child->nodeTag << ";" << std::endl;
				index++;
				break;
			case OR_T:
				os << "formulas[" << index << "].type = OR_T;" << std::endl;
				os << "formulas[" << index << "].val.children.lchild = " << (*it)->val.binOp.lchild->nodeTag << ";" << std::endl;
				os << "formulas[" << index << "].val.children.rchild = " << (*it)->val.binOp.rchild->nodeTag << ";" << std::endl;
				index++;
				break;
			case UNTIL_T:
				os << "formulas[" << index << "].type = UNTIL_T;" << std::endl;
				os << "formulas[" << index << "].val.t_children.lchild = " << (*it)->val.twotempOp.lchild->nodeTag << ";" << std::endl;
				os << "formulas[" << index << "].val.t_children.rchild = " << (*it)->val.twotempOp.rchild->nodeTag << ";" << std::endl;
				os << "formulas[" << index << "].val.t_children.hbound = " << (*it)->val.twotempOp.lbound << ";" << std::endl;
				os << "formulas[" << index << "].val.t_children.lbound = " << (*it)->val.twotempOp.hbound << ";" << std::endl;
				index++;
				break;
			case SINCE_T:
				os << "formulas[" << index << "].type = SINCE_T;" << std::endl;
				os << "formulas[" << index << "].val.t_children.lchild = " << (*it)->val.twotempOp.lchild->nodeTag << ";" << std::endl;
				os << "formulas[" << index << "].val.t_children.rchild = " << (*it)->val.twotempOp.rchild->nodeTag << ";" << std::endl;
				os << "formulas[" << index << "].val.t_children.hbound = " << (*it)->val.twotempOp.lbound << ";" << std::endl;
				os << "formulas[" << index << "].val.t_children.lbound = " << (*it)->val.twotempOp.hbound << ";" << std::endl;
				index++;
				break;
			default:
				break;

		}
	}
		
}

void confBuildStruct(std::vector<Node*> forms, std::ostream &os) {
	int index = 0;
	std::vector<Node*>::iterator it;
	for (it = forms.begin(); it != forms.end(); it++) {
		os << "initResStruct(&theStruct[" << index << "], " << (*it)->nodeTag << ", FORM_DELAY, &rbuffers[" << index << "], &ibuffers[" << index << "][0], &ibuffers[" << index << "][1]);" << std::endl;
		index++;
	}
}

void confBuildSimpTables(int nforms, std::vector<Node*> list, std::ostream &os) {
		///// SIMPLIFICATION TABLE STUFF
		std::vector<Node*>::iterator it;
		int NFORMULAS = nforms;
		int notForms[NFORMULAS];
		int orForms[NFORMULAS][NFORMULAS];
		int untilForms[NFORMULAS][NFORMULAS];
		int sinceForms[NFORMULAS][NFORMULAS];
		int si, si2;
		// initialize simplification tables:
		for (si = 0; si < NFORMULAS; si++) {
			notForms[si] = 0;
			// 2-dimensional ones
			for (si2 = 0; si2 < NFORMULAS; si2++) {
				orForms[si][si2] = 0;
				untilForms[si][si2] = 0;
				sinceForms[si][si2] = 0;
			}
		}

		// do true/false filling:
		// fill NOT 1/2
		notForms[1] = 2; // not false is true
		notForms[2] = 1; // not true is false
		// fill OR:
		// true row is true
		// DON'T DO 0 -- we want to leave INVALID invalid
		for (si = 1; si < NFORMULAS; si++) {
			orForms[2][si] = 2;
			orForms[si][2] = 2;
		}
		// false row is pass-through
		// DON'T DO 0 -- we want to leave INVALID invalid
		for (si = 1; si < NFORMULAS; si++) {
			orForms[1][si] = si;
			orForms[si][1] = si;
		}

		// fill simplification tables
		for (it = list.begin(); it!=list.end(); it++) {
			if ((*it)->type == NOT_T) {
				notForms[(*it)->val.child->nodeTag] = (*it)->nodeTag;
			} else if ((*it)->type == OR_T) {
				orForms[(*it)->val.binOp.lchild->nodeTag][(*it)->val.binOp.rchild->nodeTag] = (*it)->nodeTag;
			} else if ((*it)->type == UNTIL_T) {
				untilForms[(*it)->val.twotempOp.lchild->nodeTag][(*it)->val.twotempOp.rchild->nodeTag] = (*it)->nodeTag;
			} else if ((*it)->type == SINCE_T) {
				sinceForms[(*it)->val.twotempOp.lchild->nodeTag][(*it)->val.twotempOp.rchild->nodeTag] = (*it)->nodeTag;
			}
		}
		// PRINT NOT
		std::cout << "const formula notForms[NFORMULAS] = {";
		for (si = 0; si < NFORMULAS; si++) {
			std::cout << notForms[si] << ",";
		}
		std::cout << "};" << std::endl;
		// PRINT OR
		std::cout << "const formula orForms[NFORMULAS][NFORMULAS] = {";
		for (si = 0; si < NFORMULAS; si++) {
			std::cout << "{";
			for (si2 = 0; si2 < NFORMULAS; si2++) {
				std::cout << orForms[si][si2] << ",";
			}
			std::cout << "}," << std::endl;
		}
		std::cout << "};" << std::endl;
		// PRINT UNTIL
		std::cout << "const formula untilForms[NFORMULAS][NFORMULAS] = {";
		for (si = 0; si < NFORMULAS; si++) {
			std::cout << "{";
			for (si2 = 0; si2 < NFORMULAS; si2++) {
				std::cout << untilForms[si][si2] << ",";
			}
			std::cout << "}," << std::endl;
		}
		std::cout << "};" << std::endl;

		// PRINT SINCE
		std::cout << "const formula sinceForms[NFORMULAS][NFORMULAS] = {";
		for (si = 0; si < NFORMULAS; si++) {
			std::cout << "{";
			for (si2 = 0; si2 < NFORMULAS; si2++) {
				std::cout << sinceForms[si][si2] << ",";
			}
			std::cout << "}," << std::endl;
		}
		std::cout << "};" << std::endl;

}
void yyerror(const char *s) {
	std::cout << "!! Parser error! Message " << s << std::endl;
	exit(-1);
}
