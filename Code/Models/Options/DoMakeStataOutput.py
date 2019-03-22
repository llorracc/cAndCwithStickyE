'''
This file sets options so that tables and figures that are produced in Stata are
reproduced on this execution.  It can only be run if Stata *is* available on the
local computer, otherwise execution will fail.  Please set the stata_exe option
in USER_OPTIONS.py to point to the Stata executable on your computer.
'''

make_emp_table = True    # Whether to run regressions for the U.S. empirical table (automatically done in Stata)
make_histogram = True    # Whether to construct the histogram of "habit" parameter estimates (automatically done in Stata)
