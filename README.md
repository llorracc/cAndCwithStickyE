---
title: "Sticky Expectations and Consumption Dynamics"
author: "Christopher Carroll, Edmund Crawley, Jiri Slacalek, Kiichi Tokuoka, Matthew White"
date: 2018/02/24

---
# Sticky Expectations and Consumption Dynamics

## Abstract

Macroeconomic models often invoke consumption 'habits' to explain the substantial persistence of aggregate consumption growth, but a large literature has found essentially no evidence of habits in micro data.  We show that the apparent conflict can be explained using a model in which consumers have accurate knowledge of their personal circumstances but 'sticky expectations' about the macroeconomy. Aggregate consumption growth exhibits persistence generated by consumers' imperfect attention to aggregate shocks, even though at the individual level consumption growth appears to be serially uncorrelated (because it is dominated by idiosyncratic shocks). In contrast with models in the existing literature, our model is consistent with _both_ micro _and_ macro stylized facts about consumption dynamics.


## Replication

-- to produce pdf version of the paper, 
   pdflatex cAndCwithStickyE.tex in this folder 

-- to replicate  all of the tables, figures, and results that appear in the paper: 
1. Go to www.continuum.io, install Anaconda for Python 2
2. Run Spyder, and open ./Software/Models/StickyE_main.py
3. Set boolean flags (False or True) to choose which results to produce
4. Run the code by clicking the green arrow button

See also ./Software/Models/README.txt for a detailed description of the project files and how to reproduce all of the tables, figures, and results in the paper. The vast majority of the project is written in Python 2.7, but some empirical work uses Stata.  

See ./Software/README.txt for a description about the folder structure under ./Software


