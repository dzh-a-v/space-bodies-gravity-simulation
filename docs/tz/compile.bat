latexmk -xelatex -outdir=out tz.tex
rd .\tz.pdf
move out\tz.pdf .\tz.pdf