'''
This file sets options so that the main results are actually produced.  There is
little reason for users to ever set these to False, as the MAIN file will not do
much if the main steps (solving the model, writing simulated data to disk, making
regression tables, and calculating microeconomic statistics) are not run.
'''

# Choose what kind of work to do for each model
run_models = True        # Whether to solve models and generate new simulated data
calc_micro_stats = True  # Whether to calculate microeconomic statistics (only matters when run_models is True)
make_tables = True       # Whether to make LaTeX tables in the /Tables folder
save_data = True         # Whether to save data for use in regressions (as a tab-delimited text file)