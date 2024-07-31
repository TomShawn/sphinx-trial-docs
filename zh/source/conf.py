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
release = 'v1.6.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'rst2pdf.pdfbuilder',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.intersphinx',
    'sphinx_tabs.tabs',
    'docxbuilder',
    'sphinx_material'
]
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

master_doc = 'index'
templates_path = ['_templates']

needs_sphinx = '3.0'
language = 'zh_CN'
autosectionlabel_prefix_document = True
# templates_path = ['_templates']

# -- HTML configuration ---------------------------------------------------

# Required theme setup

html_theme = 'sphinx_material'
html_title = 'HashData Lightning 用户文档'

html_theme_options = {
    # 'base_url': base_url,
    'color_primary': 'blue',
    'color_accent': 'blue',
    'logo_icon': '&#xe150',
    'master_doc': False,

    # Set you GA account ID to enable tracking
    # 'google_analytics_account': '142118122',

    # Set the repo location to get a badge with stats
    'repo_url': 'https://github.com/TomShawn/sphinx-trial-docs',
    'repo_name': 'sphinx-trial-docs',

    # Visible levels of the global TOC; -1 means unlimited
    'globaltoc_depth': 4,
    # If False, expand all TOC entries
    'globaltoc_collapse': True,
    # If True, show hidden TOC entries
    'globaltoc_includehidden': False,

    'show_theme_credit': False
}

html_theme_path = sphinx_material.html_theme_path()
html_context = sphinx_material.get_html_context()
html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}

html_static_path = ['_static']
templates_path = ['_templates']

# html_theme = "sphinx_rtd_theme"
# html_logo = './images/hashdata-logo.png'

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


\usepackage{fancyhdr}
\usepackage{graphicx}
\pagestyle{fancy}

% 清除默认设置
\fancyhf{}

% 调整章节标题格式，防止页眉和章节标题重叠
\usepackage{titlesec}

% 自定义页脚格式
\fancyfoot[R]{\chaptername\ \thechapter：\nouppercase{\rightmark}}

% 设置 chapter 标题居中，并使用“第 X 章”格式
\titleformat{\chapter}[display]
{\normalfont\LARGE\bfseries\centering}{第 \thechapter 章}{60pt}{\Huge}
\titlespacing*{\chapter}{0pt}{50pt}{40pt}

% 自定义章节标题格式
\renewcommand{\chaptermark}[1]{\markboth{#1}{}}

'''
}
