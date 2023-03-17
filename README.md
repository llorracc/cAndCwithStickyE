---
title: "Sticky Expectations and Consumption Dynamics"
author: "Christopher Carroll, Edmund Crawley, Jiri Slacalek, Kiichi Tokuoka, Matthew White"
date: 2019/05/21

---
# Sticky Expectations and Consumption Dynamics

## Abstract

To match aggregate consumption dynamics, macroeconomic models must generate `excess smoothness' in consumption expenditures.   But microfounded models are calibrated to match micro data, which exhibit no `excess smoothness.' So standard microfounded models fail to match the macro smoothness facts.  We show that the micro and macro evidence are both consistent with a microfounded model where consumers know their personal circumstances but have `sticky expectations' about the macroeconomy.  Aggregate consumption sluggishness reflects consumers' imperfect attention to aggregate shocks. Our proposed degree of inattention has negligible utility costs because aggregate shocks constitute a tiny proportion of the uncertainty that consumers face.

## Replication

-- to produce pdf version of the paper, 
   pdflatex cAndCwithStickyE.tex in this folder 

-- to replicate all of the tables, figures, and results that appear in the paper: 
1. Install Anaconda for Python 3 
2. In the Anaconda terminal (Windows) or Unix-like terminal (other OS):
    - Navigate to the root of this archive.
    - run "pip install -r requirements.txt"
3. Open ./USER_OPTIONS.py and set three simple options there; defaults work fine
4. Run Spyder, and open ./do_all.py
5. Run the code by clicking the green arrow button; this will take 1-2 days to run

Running do_min.py or do_mid.py will produce subsets of the results in the paper, taking less than a minute and about 30 minutes respectively.  The file do_custom.py explicitly lists all boolean parameters needed to run the MAIN code file, so that you can customize the work that is done on an execution run.

See also ./Code/Models/README.txt for a detailed description of the project files and how to reproduce all of the tables, figures, and results in the paper. The vast majority of the project is written in Python, but some empirical work uses Stata.  

See ./Code/README.txt for a description about the folder structure under ./Code


