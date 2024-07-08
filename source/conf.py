# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
import sphinx_material

sys.path.insert(0, os.path.abspath('.'))
sys.path.append('.')

project = 'HashData Lightning 文档'
copyright = '2024, HashData'
author = 'HashData'
release = 'latest'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
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

needs_sphinx = '3.0'
language = 'zh_CN'
autosectionlabel_prefix_document = True
templates_path = ['_templates']

# -- HTML configuration ---------------------------------------------------

# Required theme setup
html_theme = 'piccolo_theme'

# # Set link name generated in the top bar.
# html_title = 'HashData Lightning 用户文档'

# # Material theme options (see theme.conf for more information)
# html_theme_options = {

#     # Set the name of the project to appear in the navigation.
#     'nav_title': 'HashData Lightning 用户文档',

#     # Specify a base_url used to generate sitemap.xml. If not
#     # specified, then no sitemap will be built.
#     #'base_url': 'https://project.github.io/project',

#     # Set the color and the accent color
#     'color_primary': 'blue',
#     'color_accent': 'light-blue',

#     # Set the repo location to get a badge with stats
#     'repo_url': 'https://github.com/TomShawn/sphinx-trial-docs/',
#     'repo_name': 'sphinx-trial-docs',

#     # Visible levels of the global TOC; -1 means unlimited
#     'globaltoc_depth': 3,
#     # If False, expand all TOC entries
#     'globaltoc_collapse': False,
#     # If True, show hidden TOC entries
#     'globaltoc_includehidden': True,
# }

# html_theme_path = sphinx_material.html_theme_path()
# html_context = sphinx_material.get_html_context()
# html_sidebars = {
#     "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
# }

# -- PDF/LaTeX configuration ---------------------------------------------------

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

% \titleformat{\chapter}[block]{\LARGE\bfseries}{\thechapter}{1em}{}
% \titleformat{\section}[block]{\Large\bfseries}{\thesection}{1em}{}
% \titleformat{\subsection}[block]{\large\bfseries}{\thesubsection}{1em}{}
% \titleformat{\subsubsection}[block]{\normalsize\bfseries}{\thesubsubsection}{1em}{}
\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{3}
\usepackage[document]{ragged2e}
\usepackage{titlesec}

% 设置一级标题（section）带有序号
\titleformat{\section}{\normalfont\Large\bfseries}{\thesection}{1em}{}

% 设置二级标题（subsection）带有序号
\titleformat{\subsection}{\normalfont\large\bfseries}{\thesubsection}{1em}{}

% 设置三级标题（subsubsection）不带序号
\titleformat{\subsubsection}[block]{\normalfont\normalsize\bfseries}{}{0pt}{}

% 取消三级以下标题的序号
\setcounter{secnumdepth}{1}

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

\usepackage{multirow}
'''
}
