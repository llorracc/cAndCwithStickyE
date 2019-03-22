'''
This file sets options so that the main results are not produced on this run.
It is unlikely the user will ever find it productive to use this set of options.
'''

# Choose what kind of work to do for each model
run_models = False       # Whether to solve models and generate new simulated data
calc_micro_stats = False # Whether to calculate microeconomic statistics (only matters when run_models is True)
make_tables = False      # Whether to make LaTeX tables in the /Tables folder
save_data = False        # Whether to save data for use in regressions (as a tab-delimited text file)
