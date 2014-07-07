# make parser
bmtl.tab.c bmtl.tab.h: bmtl.y
	bison -d bmtl.y

lex.yy.c: bmtl.l bmtl.tab.h
	flex bmtl.l

bmtl: lex.yy.c bmtl.tab.c bmtl.tab.h
	g++ bmtl.tab.c lex.yy.c -o bmtl
