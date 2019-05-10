'''
This module holds calibrated parameter dictionaries for the cAndCwithStickyE paper.
It defines dictionaries for the six types of models in cAndCwithStickyE:

1) Small open economy
2) Small open Markov economy
3) Cobb-Douglas closed economy
4) Cobb-Douglas closed Markov economy
5) Representative agent economy
6) Markov representative agent economy

For the first four models (heterogeneous agents), it defines dictionaries for
the Market instance as well as the consumers themselves.  All parameters are quarterly.
'''
from __future__ import division
from builtins import range
from past.utils import old_div
import os
import numpy as np
from copy import copy
from HARK.utilities import approxUniform, approxMeanOneLognormal, combineIndepDstns

# Choose directory paths relative to the StickyE files
# See: https://stackoverflow.com/questions/918154/relative-paths-in-python
my_file_path = os.path.dirname(os.path.abspath(__file__))

calibration_dir = os.path.join(my_file_path, "../../Calibration/Parameters/") # Absolute directory for primitive parameter files
tables_dir = os.path.join(my_file_path, "../../Tables/")       # Absolute directory for saving tex tables
results_dir = os.path.join(my_file_path, "./Results/")         # Absolute directory for saving output files
figures_dir = os.path.join(my_file_path, "../../Figures/")     # Absolute directory for saving figures
empirical_dir = os.path.join(my_file_path, "../Empirical/")    # Absolute directory with empirical files

def importParam(param_name):
    return float(np.max(np.genfromtxt(calibration_dir + param_name + '.txt')))

# Import primitive parameters from calibrations folder
CRRA = importParam('CRRA')                   # Coefficient of relative risk aversion
DeprFacAnn = importParam('DeprFacAnn')       # Annual depreciation factor
CapShare = importParam('CapShare')           # Capital's share in production function
KYratioSS = importParam('KYratioSS')         # Steady state capital to output ratio (PF-DSGE)
UpdatePrb = importParam('UpdatePrb')         # Probability that each agent observes the aggregate productivity state each period (in sticky version)
UnempPrb = importParam('UnempPrb')           # Unemployment probability
DiePrb = importParam('DiePrb')               # Quarterly mortality probability
TranShkVarAnn = importParam('TranShkVarAnn') # Annual variance of idiosyncratic transitory shocks
PermShkVarAnn = importParam('PermShkVarAnn') # Annual variance of idiosyncratic permanent shocks
TranShkAggVar = importParam('TranShkAggVar') # Variance of aggregate transitory shocks
PermShkAggVar = importParam('PermShkAggVar') # Variance of aggregate permanent shocks
DiscFacSOE = importParam('betaSOE')          # Discount factor, SOE model

# Calculate parameters based on the primitive parameters
DeprFac = 1. - DeprFacAnn**0.25                  # Quarterly depreciation rate
KSS = KtYratioSS = KYratioSS**(1./(1.-CapShare)) # Steady state Capital to labor productivity
wRteSS = (1.-CapShare)*KSS**CapShare             # Steady state wage rate
rFreeSS = CapShare*KSS**(CapShare-1.)            # Steady state interest rate
RfreeSS = 1. - DeprFac + rFreeSS                 # Steady state return factor
LivPrb = 1. - DiePrb                             # Quarterly survival probability
DiscFacDSGE = RfreeSS**(-1)                      # Discount factor, HA-DSGE and RA models
TranShkVar = TranShkVarAnn*4.                    # Variance of idiosyncratic transitory shocks
PermShkVar = old_div(PermShkVarAnn,4.)           # Variance of idiosyncratic permanent shocks

# Choose basic simulation parameters
periods_to_sim = 21010 # Total number of periods to simulate; this might be increased by DSGEmarkov model
ignore_periods = 1000  # Number of simulated periods to ignore (in order to ensure we are near steady state)
interval_size = 200    # Number of periods in each subsample interval
AgentCount = 20000     # Total number of agents to simulate in the economy
max_t_between_updates = None # Maximum number of periods an agent will go between updating (can be None)

# Use smaller sample for micro regression tables to save memory
periods_to_sim_micro = 4000
AgentCount_micro = 5000

# Choose extent of discount factor heterogeneity (inapplicable to representative agent models)
# These parameters are used in all specifications of the main text
TypeCount = 1                  # Number of heterogeneous discount factor types
DiscFacMeanSOE  = DiscFacSOE   # Central value of intertemporal discount factor for SOE model
DiscFacMeanDSGE = DiscFacDSGE  # ...for HA-DSGE and RA
DiscFacSpread = 0.0            # Half-width of intertemporal discount factor band, a la cstwMPC
IncUnemp = 0.0                 # Zero unemployment benefits as baseline

# These parameters were estimated to match the distribution of liquid wealth a la
# cstwMPC in the file BetaDistEstimation.py; these use unemployment benefits of 30%.
# To reproduce the excess sensitivity experiment in the paper, uncomment these lines.
TypeCount_parker = 11
DiscFacMeanSOE_parker = 0.93286
DiscFacMeanDSGE_parker = 0.93286
DiscFacSpread_parker = 0.0641
IncUnemp_parker = 0.3

# Choose parameters for the Markov models
StateCount = 11         # Number of discrete states in the Markov specifications
PermGroFacMin = 0.9925  # Minimum value of aggregate permanent growth in Markov specifications
PermGroFacMax = 1.0075  # Maximum value of aggregate permanent growth in Markov specifications
Persistence = 0.5       # Base probability that macroeconomic Markov state stays the same; else moves up or down by 1
RegimeChangePrb = 0.00  # Probability of "regime change", randomly jumping to any Markov state (not used in paper)

# Make the Markov array with chosen states, persistence, and regime change probability
PolyMrkvArray = np.zeros((StateCount,StateCount))
for i in range(StateCount):
    for j in range(StateCount):
        if i==j:
            PolyMrkvArray[i,j] = Persistence
        elif (i==(j-1)) or (i==(j+1)):
            PolyMrkvArray[i,j] = 0.5*(1.0 - Persistence)
PolyMrkvArray[0,0] += 0.5*(1.0 - Persistence)
PolyMrkvArray[StateCount-1,StateCount-1] += 0.5*(1.0 - Persistence)
PolyMrkvArray *= 1.0 - RegimeChangePrb
PolyMrkvArray += RegimeChangePrb/StateCount

# Define the set of aggregate permanent growth factors that can occur (Markov specifications only)
PermGroFacSet = np.exp(np.linspace(np.log(PermGroFacMin),np.log(PermGroFacMax),num=StateCount))

# Make an alternative version of the Markov array in which agents believe that their "sticky expectations"
# is actually the true shock structure.  That is, that the aggregate state only changes with prob UpdatePrb,
# but that the state changes are as if ~1/UpdatePrb periods have elapsed.
t_exp_between_updates = int(np.round(1./UpdatePrb))
PolyMrkvArrayAlt = PolyMrkvArray
for t in range(t_exp_between_updates-1): # Premultiply T-1 times
    PolyMrkvArrayAlt = np.dot(PolyMrkvArray,PolyMrkvArrayAlt)
PolyMrkvArrayAlt *= UpdatePrb # Scale down all transitions so they only happen with UpdatePrb probability
PolyMrkvArrayAlt += (1.-UpdatePrb)*np.eye(StateCount) # Move that probability weight to no change
    
# In the alternate specification, agents also think that permanent aggregate shocks only
# happen with UpdatePrb probability, but are 1/UpdatePrb times larger when they do happen.
# Transitory aggregate shocks are interpreted to be much larger when not updating.
PermShkAggVarAlt = PermShkAggVar/UpdatePrb
PermShkAggStdAlt = np.sqrt(PermShkAggVarAlt)
PermShkAggDstnAlt_update = approxMeanOneLognormal(5,PermShkAggStdAlt)
TranShkAggDstnAlt_update = approxMeanOneLognormal(5,np.sqrt(TranShkAggVar))
AggShkDstnAlt_update = combineIndepDstns(PermShkAggDstnAlt_update,TranShkAggDstnAlt_update)
AggShkDstnAlt_update[0] *= UpdatePrb
PermShkAggDstnAlt_dont = [np.array([1.0]),np.array([1.0])] # Degenerate distribution
TranShkAggDstnAlt_dont = approxMeanOneLognormal(5,np.sqrt(TranShkAggVar + PermShkAggVar/UpdatePrb))
AggShkDstnAlt_dont = combineIndepDstns(PermShkAggDstnAlt_dont,TranShkAggDstnAlt_dont)
AggShkDstnAlt_dont[0] *= 1.-UpdatePrb
AggShkDstnAlt = StateCount*[[np.concatenate([AggShkDstnAlt_update[n],AggShkDstnAlt_dont[n]]) for n in range(3)]]


# Define the set of discount factors that agents have (for SOE and DSGE models)
DiscFacSetSOE  = approxUniform(N=TypeCount,bot=DiscFacMeanSOE-DiscFacSpread,top=DiscFacMeanSOE+DiscFacSpread)[1]
DiscFacSetDSGE = approxUniform(N=TypeCount,bot=DiscFacMeanDSGE-DiscFacSpread,top=DiscFacMeanDSGE+DiscFacSpread)[1]
DiscFacSetSOE_parker  = approxUniform(N=TypeCount_parker,
                                      bot=DiscFacMeanSOE_parker-DiscFacSpread_parker,
                                      top=DiscFacMeanSOE_parker+DiscFacSpread_parker)[1]

###############################################################################

# Define parameters for the small open economy version of the model
init_SOE_consumer = { 'CRRA': CRRA,
                      'DiscFac': DiscFacMeanSOE,
                      'LivPrb': [LivPrb],
                      'PermGroFac': [1.0],
                      'AgentCount': AgentCount // TypeCount, # Spread agents evenly among types
                      'aXtraMin': 0.00001,
                      'aXtraMax': 40.0,
                      'aXtraNestFac': 3,
                      'aXtraCount': 48,
                      'aXtraExtra': [None],
                      'PermShkStd': [np.sqrt(PermShkVar)],
                      'PermShkCount': 7,
                      'TranShkStd': [np.sqrt(TranShkVar)],
                      'TranShkCount': 7,
                      'UnempPrb': UnempPrb,
                      'UnempPrbRet': 0.0,
                      'IncUnemp': IncUnemp,
                      'IncUnempRet': 0.0,
                      'BoroCnstArt':0.0,
                      'tax_rate':0.0,
                      'T_retire':0,
                      'MgridBase': np.array([0.5,1.5]),
                      'aNrmInitMean' : np.log(0.00001),
                      'aNrmInitStd' : 0.0,
                      'pLvlInitMean' : 0.0,
                      'pLvlInitStd' : 0.0,
                      'UpdatePrb' : UpdatePrb,
                      'T_age' : None,
                      'T_cycle' : 1,
                      'cycles' : 0,
                      'T_sim' : periods_to_sim,
                       'max_t_between_updates' : max_t_between_updates
                    }

# Define market parameters for the small open economy
init_SOE_market = {  'PermShkAggCount': 5,
                     'TranShkAggCount': 5,
                     'PermShkAggStd': np.sqrt(PermShkAggVar),
                     'TranShkAggStd': np.sqrt(TranShkAggVar),
                     'PermGroFacAgg': 1.0,
                     'DeprFac': DeprFac,
                     'CapShare': CapShare,
                     'Rfree': RfreeSS,
                     'wRte': wRteSS,
                     'act_T': periods_to_sim,
                     }

###############################################################################

# Define parameters for the small open Markov economy version of the model
init_SOE_mrkv_consumer = copy(init_SOE_consumer)
init_SOE_mrkv_consumer['MrkvArray'] = PolyMrkvArray
init_SOE_mrkv_consumer['MrkvArrayAlt'] = PolyMrkvArrayAlt
init_SOE_mrkv_consumer['AggShkDstnAlt'] = AggShkDstnAlt

# Define market parameters for the small open Markov economy
init_SOE_mrkv_market = copy(init_SOE_market)
init_SOE_mrkv_market['MrkvArray'] = PolyMrkvArray
init_SOE_mrkv_market['PermShkAggStd'] = StateCount*[init_SOE_market['PermShkAggStd']]
init_SOE_mrkv_market['TranShkAggStd'] = StateCount*[init_SOE_market['TranShkAggStd']]
init_SOE_mrkv_market['PermGroFacAgg'] = PermGroFacSet
init_SOE_mrkv_market['MrkvNow_init'] = StateCount // 2
init_SOE_mrkv_market['loops_max'] = 1

###############################################################################

# Define parameters for the Cobb-Douglas DSGE version of the model
init_DSGE_consumer = copy(init_SOE_consumer)
init_DSGE_consumer['DiscFac'] = DiscFacMeanDSGE
init_DSGE_consumer['aXtraMax'] = 120.0
init_DSGE_consumer['MgridBase'] = np.array([0.1,0.3,0.5,0.6,0.7,0.8,0.9,0.98,1.0,1.02,1.1,1.2,1.3,1.4,1.5,1.6,2.0,3.0,5.0])

# Define market parameters for the Cobb-Douglas economy
init_DSGE_market = copy(init_SOE_market)
init_DSGE_market.pop('Rfree')
init_DSGE_market.pop('wRte')
init_DSGE_market['CRRA'] = CRRA
init_DSGE_market['DiscFac'] = DiscFacMeanDSGE
init_DSGE_market['intercept_prev'] = 0.0
init_DSGE_market['slope_prev'] = 1.0
init_DSGE_market['DampingFac'] = 0.2

###############################################################################

# Define parameters for the Cobb-Douglas Markov DSGE version of the model
init_DSGE_mrkv_consumer = copy(init_DSGE_consumer)
init_DSGE_mrkv_consumer['MrkvArray'] = PolyMrkvArray

# Define market parameters for the Cobb-Douglas Markov economy
init_DSGE_mrkv_market = copy(init_SOE_mrkv_market)
init_DSGE_mrkv_market.pop('Rfree')
init_DSGE_mrkv_market.pop('wRte')
init_DSGE_mrkv_market['CRRA'] = init_DSGE_mrkv_consumer['CRRA']
init_DSGE_mrkv_market['DiscFac'] = init_DSGE_mrkv_consumer['DiscFac']
init_DSGE_mrkv_market['intercept_prev'] = StateCount*[0.0]
init_DSGE_mrkv_market['slope_prev'] = StateCount*[1.0]
init_DSGE_mrkv_market['loops_max'] = 10

###############################################################################

# Define parameters for the representative agent version of the model
init_RA_consumer =  { 'CRRA': CRRA,
                      'DiscFac': DiscFacMeanDSGE,
                      'LivPrb': [1.0],
                      'PermGroFac': [1.0],
                      'AgentCount': 1,
                      'aXtraMin': 0.00001,
                      'aXtraMax': 120.0,
                      'aXtraNestFac': 3,
                      'aXtraCount': 48,
                      'aXtraExtra': [None],
                      'PermShkStd': [np.sqrt(PermShkAggVar)],
                      'PermShkCount': 7,
                      'TranShkStd': [np.sqrt(TranShkAggVar)],
                      'TranShkCount': 7,
                      'UnempPrb': 0.0,
                      'UnempPrbRet': 0.0,
                      'IncUnemp': 0.0,
                      'IncUnempRet': 0.0,
                      'BoroCnstArt':0.0,
                      'tax_rate':0.0,
                      'T_retire':0,
                      'aNrmInitMean' : np.log(0.00001),
                      'aNrmInitStd' : 0.0,
                      'pLvlInitMean' : 0.0,
                      'pLvlInitStd' : 0.0,
                      'PermGroFacAgg' : 1.0,
                      'UpdatePrb' : UpdatePrb,
                      'CapShare' : CapShare,
                      'DeprFac' : DeprFac,
                      'T_age' : None,
                      'T_cycle' : 1,
                      'T_sim' : periods_to_sim,
                      'tolerance' : 1e-6
                    }

###############################################################################

# Define parameters for the Markov representative agent model
init_RA_mrkv_consumer = copy(init_RA_consumer)
init_RA_mrkv_consumer['MrkvArray'] = PolyMrkvArray
init_RA_mrkv_consumer['MrkvNow'] = [StateCount // 2]
init_RA_mrkv_consumer['PermGroFac'] = [PermGroFacSet]
