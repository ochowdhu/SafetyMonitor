# make parser
bmtl.tab.c bmtl.tab.h: bmtl.y
	bison -d bmtl.y

lex.yy.c: bmtl.l bmtl.tab.h
	flex bmtl.l

bmtl: lex.yy.c bmtl.tab.c bmtl.tab.h
	g++ bmtl.tab.c lex.yy.c -o bmtl


### make new parser
bmtl2.tab.c bmtl2.tab.h: bmtl2.y
	bison -d bmtl2.y

bmtl2: lex.yy.c bmtl2.tab.c bmtl2.tab.h
	g++ bmtl2.tab.c lex.yy.c -o bmtl2
