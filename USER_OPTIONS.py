'''
This file contains three options that the user should set before running any of
the do_XXX.py files for this project.  It is run by every do_XXX.py file to allow
the code to run correctly on the user's computer.

verbose_main indicates whether figures should be displayed to screen when running.
This should only be set to True if the users is running in a graphical environment
like iPython (recommended).  If set to True in "vanilla Python", figures will halt
execution until the user closes the window.

use_stata indicates whether the code should use Stata to run regressions rather 
than do this in Python itself.  Results from the Stata version are reported in
the paper; Python versions of the regressions are unable to produce the KP statistic;
Python's statsmodels.api currently does not have this functionality.  Results
differ slightly due to small differences in how lagged variables are handled.

stata_exe indicates where the Stata executable can be found.  This should point at
the exe file itself, but the string does not need to include '.exe'.  Two examples
are included (for locations on two authors' local computers).  This variable
is irrelevant when use_stata is set to False.

NOTE: To successfully use_stata, you must have Baum, Schaffer, and Stillman's
ivreg2 Stata module installed, as well as Kleibergen and Schaffer's ranktest
module.  These modules are archived by RePEc IDEAS at:
https://ideas.repec.org/c/boc/bocode/s425401.html
https://ideas.repec.org/c/boc/bocode/s456865.html
You can also simply type "ssc install ivreg2" and "ssc install ranktest" in Stata.
'''

verbose_main = False     # Whether to display figures to screen; this should only be True when in a graphical environment like iPython
use_stata = False        # Whether to use Stata to run the simulated time series regressions
stata_exe = "C:\Program Files (x86)\Stata15\StataSE-64"  # Location of Stata executable
#stata_exe = "C:\Program Files (x86)\Stata14\StataMP-64" # Alternate location on a different computer
