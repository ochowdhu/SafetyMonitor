%{
#include <cstdio>
#include <iostream>
#define YY_DECL extern "C" int yylex()

#include "bmtl.tab.h"
%}

%option noyywrap

%%
[ \t]	;
true	{ yylval.bval = true; return VALUE; }
false	{ yylval.bval = false; return VALUE; }
[_a-zA-Z][_a-zA-Z0-9]*	{yylval.sval = strdup(yytext); return PROP;}
[0-9]+	{ yylval.ival = atoi(yytext); return BOUND;}
"~"		{return NOT;}
"&&"	{ return AND;}
"||"	{ return OR;}
"->"	{ return IMPLIES; }
[\n\r]+		{ return ENDL; }
")"		{ return ')';}
"("		{ return '(';}
","		{ return ',';}

"["		{ return ALWAYS_L;}
"]"		{ return ALWAYS_R;}
"[["		{ return PALWAYS_L;}
"]]"		{ return PALWAYS_R;}
"$"		{ return SINCE; }
"$$"	{ return UNTIL; }
"<"		{ return EVENT_L;}
">"		{ return EVENT_R;}
"<<"		{ return PEVENT_L;}
">>"		{ return PEVENT_R;}
%%
