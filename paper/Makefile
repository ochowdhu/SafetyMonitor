	input=paper

all:
	latex $(input)
	-bibtex $(input)
	latex $(input)
	latex $(input)
	dvips -u +ltlfonts.map -Ppdf -G0  -o $(input).ps $(input).dvi
	ps2pdf  $(input).ps

win:
	latex $(input)
	-bibtex $(input)
	latex $(input)
	latex $(input)
	dvipdfmx -p letter $(input)

clean:
	rm -f *.ps *.aux *.lof *.lot *.out *.log *.dvi *.bbl *.toc *.blg  *~ 
