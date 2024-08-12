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

project = 'HashData Lightning Documentation'
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
    'docxbuilder'
]
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

master_doc = 'index-main'

needs_sphinx = '3.0'
language = 'en'
autosectionlabel_prefix_document = True
# templates_path = ['_templates']

# -- HTML configuration ---------------------------------------------------

# Required theme setup
html_theme = "sphinx_rtd_theme"


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
% \newcommand{\sectionbreak}{\clearpage}
\usepackage[none]{hyphenat}
\renewcommand{\cftsecnumwidth}{2.5em}
\renewcommand{\cftsubsecnumwidth}{3.5em}
\renewcommand{\cftsubsubsecnumwidth}{4.5em}


\setcounter{secnumdepth}{3}
\setcounter{tocdepth}{3}
\usepackage[document]{ragged2e}
\usepackage{titlesec}
\usepackage{fancyhdr}
\setlength{\headheight}{24pt}  % 调整页眉高度
\fancyhf{}  % 清除默认的页眉和页脚

% 设置页眉和页脚
\fancyhead[R]{\rightmark}  % 页眉右侧显示文档名或章节标题
\fancyfoot[L]{\leftmark}  % 页脚左侧显示章节标题
\fancyfoot[R]{\thepage}  % 页脚右侧显示页码

\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0pt}

% 确保所有页面都使用统一的页眉和页脚设置，包括 plain 页面样式
\fancypagestyle{plain}{
    \fancyhf{}
    \fancyhead[R]{\rightmark}  % 页眉右侧显示文档名或章节标题
    \fancyfoot[L]{\leftmark}  % 页脚左侧显示章节标题
    \fancyfoot[R]{\thepage}  % 页脚右侧显示页码
    \renewcommand{\headrulewidth}{0.4pt}
    \renewcommand{\footrulewidth}{0pt}
}

% 确保所有页面都使用统一的页眉设置
\makeatletter
\let\ps@plain\ps@fancy  % 确保 plain 页面样式与 fancy 一致
\@ifundefined{if@twoside}{\newif\if@twoside}
\@twosidefalse
\makeatother

% 调整章节标题格式，防止页眉和章节标题重叠
\usepackage{titlesec}

% 设置一级标题（section）带有序号
\titleformat{\section}{\normalfont\Large\bfseries}{\thesection}{1em}{}

% 设置二级标题（subsection）带有序号
\titleformat{\subsection}{\normalfont\large\bfseries}{\thesubsection}{1em}{}

% 设置三级标题（subsubsection）不带序号
\titleformat{\subsubsection}[block]{\normalfont\normalsize\bfseries}{}{0pt}{}

% 取消三级以下标题的序号
\setcounter{secnumdepth}{1}

% 设置 chapter 标题居中，并使用“第 X 章”格式
\titleformat{\chapter}[display]
{\normalfont\Huge\bfseries\centering}{Chapter \thechapter}{60pt}{\Huge}
\titlespacing*{\chapter}{0pt}{50pt}{40pt}

% 自定义章节标题格式
\renewcommand{\chaptermark}[1]{\markboth{#1}{}}
\renewcommand{\sectionmark}[1]{\markright{#1}}


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

\usepackage{enumitem}
\setlist[itemize,1]{label=\textbullet} % 一级无序列表符号为实心圆点
\setlist[itemize,2]{label=\(\circ\)}   % 二级无序列表符号为空心小圆点

'''
}
