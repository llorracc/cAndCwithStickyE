'''
This file sets options so that tables and figures that are produced in Stata are
not made on this execution.  It should be run if Stata is *not* available on the
local computer, otherwise execution will fail.
'''

make_emp_table = False   # Whether to run regressions for the U.S. empirical table (automatically done in Stata)
make_histogram = False   # Whether to construct the histogram of "habit" parameter estimates (automatically done in Stata)
