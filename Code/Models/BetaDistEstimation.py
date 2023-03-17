'''
This module runs a some simple estimations to calibrate the distribution of discount
factors for an exercise in the StickyE paper.
'''
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from builtins import str
from builtins import range
import numpy as np
from time import clock
from copy import deepcopy
from HARK.ConsumptionSaving.ConsIndShockModel import IndShockConsumerType
from HARK.utilities import approxUniform, getLorenzShares, calcSubpopAvg
from HARK.parallel import multiThreadCommands, multiThreadCommandsFake
from HARK.estimation import minimizeNelderMead
import matplotlib.pyplot as plt
import StickyEparams as Params

if __name__ == '__main__':

    # Make a dictionary for IndShockConsumerTypes by slightly altering the SOE dictionary
    temp_dict = deepcopy(Params.init_SOE_consumer)
    temp_dict['Rfree'] = Params.init_SOE_mrkv_market['Rfree']
    temp_dict['vFuncBool'] = False
    temp_dict['CubicBool'] = False
    temp_dict['PermGroFacAgg'] = 1.0
    temp_dict['AgentCount'] = 10000
    temp_dict['IncUnemp'] = 0.3 # Set this to 0.0 (baseline) or 0.3 (to add unemployment benefits)
    temp_dict['T_sim'] = 1000
    
    make_simple_plots = False
    estimate_by_wealth = False
    estimate_by_MPC = True
    
    if make_simple_plots:
        # Make some agents to play with
        TestType = IndShockConsumerType(**temp_dict)
        
        DiscFac_vec = np.linspace(0.1,0.98,101)
        MPC_vec = np.zeros_like(DiscFac_vec)
        Wealth_vec = np.zeros_like(DiscFac_vec)
        
        t_start = clock()
        for j in range(DiscFac_vec.size):
            TestType(DiscFac = DiscFac_vec[j])
            TestType.solve()
            TestType.initializeSim()
            TestType.simulate()
            MPC_vec[j] = np.mean(TestType.MPCnow)
            Wealth_vec[j] = np.mean(TestType.aNrmNow)
            print('Finished DiscFac=' + str(DiscFac_vec[j]))
        t_end = clock()
        
        print('Solving and simulating ' + str(DiscFac_vec.size) + ' types took ' + str(t_end-t_start) + ' seconds.')
            
        plt.plot(DiscFac_vec,MPC_vec)
        plt.xlabel('Discount factor')
        plt.ylabel('Average marginal propensity to consume')
        plt.show()
        
        plt.plot(DiscFac_vec,Wealth_vec)
        plt.xlabel('Discount factor')
        plt.ylabel('Average assets to income ratio')
        plt.show()
        
    if estimate_by_wealth:
        # Define parameters for the beta-dist estimation
        TypeCount = 11
        percentile_targets = [0.2,0.4,0.6,0.8]
        
        liquid_wealth = True
        if liquid_wealth:
            aNrmMean_data = 6.6
            Lorenz_data = [0.000, 0.004, 0.025, 0.117]
        else:
            aNrmMean_data = 10.26
            Lorenz_data = [-0.002, 0.01, 0.053, 0.171]
        moments_data = np.array([aNrmMean_data] + Lorenz_data)
        
        # Make the agent types
        BaseAgent = IndShockConsumerType(**temp_dict)
        Agents = []
        for j in range(TypeCount):
            Agents.append(deepcopy(BaseAgent))
            
        # Define the objective function
        def objectiveFuncWealth(center,spread):
            '''
            Objective function of the beta-dist estimation, similar to cstwMPC.
            Minimizes the distance between simulated and actual 20-40-60-80 Lorenz
            curve points and average wealth to income ratio.
            
            Parameters
            ----------
            center : float
                Mean of distribution of discount factor.
            spread : float
                Half width of span of discount factor.
                
            Returns
            -------
            distance : float
                Distance between simulated and actual moments.
            '''
            DiscFacSet = approxUniform(N=TypeCount,bot=center-spread,top=center+spread)[1]
            for j in range(TypeCount):
                Agents[j](DiscFac = DiscFacSet[j])
                
            multiThreadCommands(Agents,['solve()','initializeSim()','simulate()'])
            aLvl_sim = np.concatenate([agent.aLvlNow for agent in Agents])
            aNrm_sim = np.concatenate([agent.aNrmNow for agent in Agents])
            
            aNrmMean_sim = np.mean(aNrm_sim)
            Lorenz_sim = list(getLorenzShares(aLvl_sim,percentiles=percentile_targets))
            
            moments_sim = np.array([aNrmMean_sim] + Lorenz_sim)
            moments_diff = moments_sim - moments_data
            moments_diff[1:] *= 1 # Rescale Lorenz shares
            distance = np.sqrt(np.dot(moments_diff,moments_diff))
            
            print('Tried center=' + str(center) + ', spread=' + str(spread) + ', got distance=' + str(distance))
            print(moments_sim)
            return distance
        
        
        def objectiveFuncWrapper(params):
            return objectiveFuncWealth(params[0],params[1])
        
        arbitrary_param_guess = [0.95,0.045]
        estimate_liquid_with_unemp_benefits = [0.93286322, 0.06410639]
        estimate_liquid_without_unemp_benefits = [0.79100088, 0.22021331]
        estimate_networth_with_unemp_benefits = [0.97150587, 0.02211607]
        estimate_netwroth_without_unemp_benefits = [0.94717781, 0.04969883]
        estimated_params = minimizeNelderMead(objectiveFuncWrapper,arbitrary_param_guess)

        
    if estimate_by_MPC:
        # Define parameters for the beta-dist estimation
        TypeCount = 11
        cutoffs = [[0.,0.2],[0.2,0.4],[0.4,0.6],[0.6,0.8],[0.8,1.0]]
        moments_data = np.array([0.833741,0.752517,0.551613,0.437491,0.232213])
        # These target moments come from Crawley
        
        # Make the agent types
        BaseAgent = IndShockConsumerType(**temp_dict)
        Agents = []
        for j in range(TypeCount):
            Agents.append(deepcopy(BaseAgent))
        
        # Define the objective function
        def objectiveFuncMPC(center,spread):
            '''
            Objective function of the beta-dist estimation, similar to cstwMPC.
            Minimizes the distance between simulated and actual mean semiannual
            MPCs by wealth quintile.
            
            Parameters
            ----------
            center : float
                Mean of distribution of discount factor.
            spread : float
                Half width of span of discount factor.
                
            Returns
            -------
            distance : float
                Distance between simulated and actual moments.
            '''
            DiscFacSet = approxUniform(N=TypeCount,bot=center-spread,top=center+spread)[1]
            for j in range(TypeCount):
                Agents[j](DiscFac = DiscFacSet[j])
                
            multiThreadCommands(Agents,['solve()','initializeSim()','simulate()'])
            aLvl_sim = np.concatenate([agent.aLvlNow for agent in Agents])
            MPC_sim = np.concatenate([agent.MPCnow for agent in Agents])
            
            MPC_alt = 1. - (1. - MPC_sim)**2
            
            MPC_by_aLvl = calcSubpopAvg(MPC_alt,aLvl_sim,cutoffs)
            
            moments_sim = MPC_by_aLvl
            moments_diff = moments_sim - moments_data
            moments_diff[1:] *= 1 # Rescale Lorenz shares
            distance = np.sqrt(np.dot(moments_diff,moments_diff))
            
            print('Tried center=' + str(center) + ', spread=' + str(spread) + ', got distance=' + str(distance))
            print(moments_sim)
            return distance
        
        
        def objectiveFuncWrapper(params):
            return objectiveFuncMPC(params[0],params[1])
        
        arbitrary_param_guess = [0.95,0.045]
        estimate_MPC_with_unemp_benefits = [0.86009922, 0.13528336]
        estimated_params = minimizeNelderMead(objectiveFuncWrapper,arbitrary_param_guess)
