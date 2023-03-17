'''
This file will run absolutely all of the results in the paper.  As fair warning,
this might take several days to run.  It runs the excess sensitivity experiment
first, then all of the SOE model exercises, then the DSGE model, then the RA model.
Please look at USER_OPTIONS.py and set three options there before proceeding.

If you have problems running it, make sure you have installed all of the packages
specified in the requirements.txt file
'''
import os
here = os.path.dirname(os.path.realpath(__file__))
my_path = os.path.join(here,'')
path_to_models = os.path.join(my_path,'Code/Models')
path_to_options = os.path.join(path_to_models,'Options')

exec(open(my_path + 'USER_OPTIONS.py').read())
os.chdir(path_to_options)
exec(open('RunSOEonly.py').read())
exec(open('DoMakeMainResults.py').read())
exec(open('DontRunExtraStuff.py').read())
exec(open('DontMakeStataOutput.py').read())
os.chdir(path_to_models)
run_parker = True # Run excess sensitivity experiment first
exec(open('StickyE_MAIN.py').read())

os.chdir(path_to_options)
exec(open('RunAllModels.py').read())
exec(open('DoMakeMainResults.py').read())
exec(open('DoRunExtraStuff.py').read())
exec(open('DoMakeStataOutput.py').read())
os.chdir(path_to_models)
run_parker = False # Don't excess sensitivity experiment this time
exec(open('StickyE_MAIN.py').read())
