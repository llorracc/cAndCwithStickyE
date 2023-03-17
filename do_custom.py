'''
This file will run a custom set of work for the project, using booleans set here
by the user.  In contrast, do_min, do_mid, and do_all use sets of execution options
specified in ./Code/Models/Options/.  As distributed, all flags are set to False,
so running this file will do very little.
'''
import os
here = os.path.dirname(os.path.realpath(__file__))
my_path = os.path.join(here,'')
path_to_models = os.path.join(my_path,'Code/Models')
path_to_options = os.path.join(path_to_models,'Options')

# Choose which models to do work for
do_SOE  = False          # Small open economy model (main text)
do_DSGE = False          # Heterogeneous agent DSGE model (appendix B)
do_RA   = False          # Representative agent model (appendix C)

# Choose what kind of work to do for each model
run_models = False       # Whether to solve models and generate new simulated data
calc_micro_stats = False # Whether to calculate microeconomic statistics (only matters when run_models is True)
make_tables = False      # Whether to make LaTeX tables in the /Tables folder
save_data = False        # Whether to save data for use in regressions (as a tab-delimited text file)

# Choose which extra exercises / experiments are run (SOE model only)
run_ucost_vs_pi = False  # Whether to run an exercise that finds the cost of stickiness as it varies with update probability
run_value_vs_aggvar = False # Whether to run an exercise to find value at birth vs variance of aggregate permanent shocks
run_alt_beliefs = False  # Whether to run an alternate specification in which agents think their sticky expectations are the true shock structure
run_parker = False       # Whether to run an experiment based on Parker & Souleles (2006)

# Choose whether to produce Table 2 and Figure 1; requires Stata
make_emp_table = False   # Whether to run regressions for the U.S. empirical table
make_histogram = False   # Whether to construct the histogram of "habit" parameter estimates

# Set options specified in USER_OPTIONS.py (sets whether graphics can be displayed,
# whether Stata can be used, and the location of the Stata executable file).
exec(open(my_path + 'USER_OPTIONS.py').read())

os.chdir(path_to_models)
exec(open('StickyE_MAIN.py').read())


