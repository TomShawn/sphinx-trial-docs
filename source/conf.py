# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys
sys.path.insert(0, os.path.abspath('.'))

project = 'HashData PDF Link Try'
copyright = '2024, Tom'
author = 'Tom'
release = '1.5.4'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'myst_parser',
    'sphinx_markdown_tables',
    'rst2pdf.pdfbuilder'
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

master_doc = 'index'

pdf_documents = [
    ('index', 'output', 'My Project', 'Author Name'),
]

# 其它 PDF 配置（可选）
# pdf_stylesheets = ['sphinx', 'kerning', 'a4']
# # pdf_break_level = 1
# pdf_breakside = 'any'
# pdf_invariant = False
# pdf_real_footnotes = True
# pdf_use_toc = True
# latex_engine = 'xelatex'
latex_elements = {
    'preamble': r'''
\usepackage{longtable}
\usepackage{xeCJK}
\usepackage{graphicx}
\usepackage{amsmath, amssymb}
\usepackage{booktabs}
\usepackage{multirow}
'''
}

language = 'zh_CN'