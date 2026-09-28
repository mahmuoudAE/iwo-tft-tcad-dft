"""Convert preamble to a plain, formal thesis style: Times (newtx) fonts, no coloured boxes, black listings/links."""
from pathlib import Path
import re
R = Path(__file__).resolve().parents[1]; p = (R / 'preamble.tex').read_text(encoding='ascii')
p = p.replace('\\usepackage{lmodern}\n', '')
p = p.replace('\\usepackage{amsmath,amssymb,amsthm,bm}', '\\usepackage{amsmath,amsthm}\n\\usepackage{newtxtext,newtxmath}   % Times text and math, as in IEEE books\n\\usepackage{bm}')
p = p.replace('\\usepackage[a4paper,margin=2.5cm,headheight=14pt]{geometry}', '\\usepackage[a4paper,top=2.5cm,bottom=2.5cm,inner=3.0cm,outer=2.5cm,headheight=14pt]{geometry}\n\\usepackage{setspace}\n\\onehalfspacing')
p = p.replace('\\captionsetup{font=small,labelfont=bf,format=hang}', '\\captionsetup{font=small,labelfont=bf,labelsep=period,format=plain}')
p = p.replace('\\fancyhead[R]{\\small IWO TFT thickness study -- TCAD}', '\\fancyhead[R]{}')
# boxed environments -> plain formal paragraphs (existing \begin{...} calls keep working; optional args are ignored)
start = p.index('% ---------------- boxed environments')
end = p.index('\\newtheorem{proposition}')
plain = r'''% ---------------- summary / note environments (plain text, no boxes or colour) ----------------
\newenvironment{keyresult}[1][]{\par\medskip\noindent\textit{Summary.}\ }{\par\medskip}
\newenvironment{statusbox}[1]{\par\medskip\noindent\textit{#1.}\ }{\par\medskip}
\newenvironment{derivation}[1][]{\par\medskip\noindent\textit{Derivation.}\ }{\par\medskip}
\newenvironment{caveat}[1][]{\par\medskip\noindent\textit{Limitation.}\ }{\par\medskip}
\newenvironment{usedbox}[1][]{\par\medskip\noindent\textit{Items used in the TCAD model.}\par}{\par\medskip}

'''
p = p[:start] + plain + p[end:]
# listings in black and grey
p = p.replace('backgroundcolor=\\color{codebg}, frame=single, rulecolor=\\color{black!25}', 'frame=lines')
p = p.replace('keywordstyle=\\color{accent}\\bfseries', 'keywordstyle=\\bfseries').replace('commentstyle=\\color{black!55}\\itshape', 'commentstyle=\\itshape').replace('stringstyle=\\color{accent2}', 'stringstyle=\\ttfamily')
p = p.replace('numberstyle=\\tiny\\color{black!45}', 'numberstyle=\\tiny')
p = p.replace('\\newcommand{\\pass}{\\textcolor{okgreen}{\\textbf{passed}}}', '\\newcommand{\\pass}{\\textbf{passed}}')
p = p.replace('\\newcommand{\\partialpass}{\\textcolor{warnamber}{\\textbf{partial}}}', '\\newcommand{\\partialpass}{\\textbf{partial}}')
p = p.replace('\\newcommand{\\fail}{\\textcolor{failred}{\\textbf{failed}}}', '\\newcommand{\\fail}{\\textbf{failed}}')
(R / 'preamble.tex').write_text(p, encoding='ascii')
m = (R / 'main.tex').read_text(encoding='ascii')
m = m.replace('{\\color{accent}\\rule{\\linewidth}{1.2pt}}', '\\rule{\\linewidth}{0.6pt}')
(R / 'main.tex').write_text(m, encoding='ascii')
print('tcolorbox left in preamble:', 'newtcolorbox' in p)
