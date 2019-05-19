'''
This file will run the absolute minimum amount of work that actually produces
relevant output-- the representative agent model in online Appendix C.  Please
look at USER_OPTIONS.py and set three options there before proceeding.

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
exec(open('RunRAonly.py').read())
exec(open('DoMakeMainResults.py').read())
exec(open('DontRunExtraStuff.py').read())
exec(open('DontMakeStataOutput.py').read())
os.chdir(path_to_models)
exec(open('StickyE_MAIN.py').read())
