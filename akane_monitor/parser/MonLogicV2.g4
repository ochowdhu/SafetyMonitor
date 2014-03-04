
grammar MonLogicV2;

/*
options {
	language = Java
}
*/


/* **********************
	Lexer Rules 
************************ */

// Names, names of propositions
NAME
	: [a-zA-Z_][a-zA-Z_0-9]*
	;

AND:		'&&' ;
OR:		'||' ;
IMPLIES:	'->' ;
NOT: 		'~' ;

BOUND: [0-9]+ ;

LALWAYS_OP : '[' ;
RALWAYS_OP : ']' ;

LEVENT_OP : '<' ;
REVENT_OP : '>' ;

LPALWAYS_OP : '[[' ;
RPALWAYS_OP : ']]' ;

LONCE_OP : '<<' ;
RONCE_OP : '>>' ;

SINCE_OP : '$' ;
UNTIL_OP: '$$' ;

// Grouping
LPAREN: '(' ;
RPAREN: ')' ;
BSEP: ',' ;

WS
	: [ \t\n\r]+ -> skip
	;


/* **********************
	Parser Rules
************************ */

//formula : exp2 ;

exp
	: tempprop
	| impprop
	;

tempprop
	: alwaysprop
	| eventprop
	| palwaysprop
	| onceprop
	| sinceprop
	| untilprop
	| until2prop
	;

/* Temporal propositions
*************************************************************************/
alwaysprop
	: (LALWAYS_OP BOUND BSEP BOUND RALWAYS_OP)? LPAREN impprop RPAREN
	;

eventprop
	: (LEVENT_OP BOUND BSEP BOUND REVENT_OP)? LPAREN impprop RPAREN
	;

untilprop
	: LPAREN impprop RPAREN UNTIL_OP BOUND BSEP BOUND UNTIL_OP LPAREN impprop RPAREN
	;

until2prop
	: UNTIL_OP BOUND BSEP BOUND UNTIL_OP LPAREN impprop RPAREN LPAREN impprop RPAREN
	;
sinceprop
	: LPAREN impprop RPAREN SINCE_OP BOUND BSEP BOUND SINCE_OP LPAREN impprop RPAREN
	;

palwaysprop
	: (LPALWAYS_OP BOUND BSEP BOUND RPALWAYS_OP)? LPAREN impprop RPAREN
	;

onceprop
	: (LONCE_OP BOUND BSEP BOUND RONCE_OP)? LPAREN impprop RPAREN
	;


/* Temp Propositions *****************************************************/


impprop
	: orprop (IMPLIES orprop)* ;
orprop
	: andprop (OR andprop)* ;
andprop
	: notprop (AND notprop)* ;
notprop
	: NOT aprop 
	| aprop 
	;
aprop 
	: nprop 
	| prop 
	//| LPAREN exp RPAREN
	| tempprop
	;
nprop : NOT NAME ;
prop : NAME ;

