# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
sys.path.append('.')

project = 'HashData Lightning 文档'
copyright = '2024, HashData'
author = 'HashData'
release = 'v1.5.4'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_markdown_tables',
    'myst_parser',
    'rst2pdf.pdfbuilder',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.intersphinx'
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

master_doc = 'index'

# pdf_documents = [
#     ('index', 'output', 'My Project', 'Author Name'),
# ]

# 其它 PDF 配置（可选）
# pdf_stylesheets = ['sphinx', 'kerning', 'a4']
# # pdf_break_level = 1
# pdf_breakside = 'any'
# pdf_invariant = False
# pdf_real_footnotes = True
# pdf_use_toc = True
needs_sphinx = '3.0'
latex_engine = 'xelatex'
latex_elements = {
    'preamble': r'''
\usepackage{longtable}
\usepackage{xeCJK}
\usepackage{graphicx}
\usepackage{amsmath, amssymb}
\usepackage{booktabs}
\usepackage{multirow}
\usepackage{titlesec}
\usepackage{tocloft}
\newcommand{\sectionbreak}{\clearpage}
\renewcommand{\cftsecnumwidth}{2.5em}
\renewcommand{\cftsubsecnumwidth}{3.5em}
\renewcommand{\cftsubsubsecnumwidth}{4.5em}
\titleformat{\chapter}[block]{\LARGE\bfseries}{\thechapter}{1em}{}
\titleformat{\section}[block]{\Large\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}[block]{\large\bfseries}{\thesubsection}{1em}{}
\titleformat{\subsubsection}[block]{\normalsize\bfseries}{\thesubsubsection}{1em}{}
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{3}
\usepackage[document]{ragged2e}

% Custom LaTeX preamble
\usepackage{etoolbox}
\makeatletter
% Override \sphinxmaketitle to remove section numbering
\patchcmd{\sphinxmaketitle}
  {\section{\MakeUppercase{\@title}}}
  {\chapter*{\MakeUppercase{\@title}}}
  {}
  {}
\makeatother
'''
}

language = 'zh_CN'