'''
Models for the cAndCwithStickyE paper, in the form of extensions to AgentType
subclasses from the ../ConsumptionSaving folder.  This module defines four new
AgentType subclasses for use in this project:

1) StickyEconsumerType: An extention of AggShockConsumerType that can be used in
    the Cobb-Douglas or small open economy specifications.
2) StickyEmarkovConsumerType: An extention of AggShockMarkovConsumerType that can
    be used in the Cobb-Douglas Markov or small open Markov economy specifications.
3) StickyErepAgent: An extention of RepAgentConsumerType that can be used in the
    representative agent specifications.
4) StickyEmarkovRepAgent: An extension of RepAgentMarkovConsumerType that can be
    used in the Markov representative agent specifications.

The Markov-based AgentTypes are imported by StickyE_MAIN, the main file for this
project.  Non-Markov AgentTypes are imported by StickyE_NO_MARKOV.
Calibrated parameters for each type are found in StickyEparams.
'''
from __future__ import division, print_function
from __future__ import absolute_import

from builtins import range, str

import numpy as np
from copy import deepcopy
from HARK.ConsumptionSaving.ConsAggShockModel import AggShockConsumerType, AggShockMarkovConsumerType,\
                CobbDouglasEconomy, CobbDouglasMarkovEconomy, SmallOpenMarkovEconomy
from HARK.ConsumptionSaving.ConsRepAgentModel import RepAgentConsumerType, RepAgentMarkovConsumerType

# Make an extension of the base type for the heterogeneous agents versions
class StickyEconsumerType(AggShockConsumerType):
    '''
    A class for representing consumers who have sticky expectations about the
    macroeconomy because they do not observe aggregate variables every period.
    '''
    def simBirth(self,which_agents):
        '''
        Makes new consumers for the given indices.  Slightly extends base method by also setting
        pLvlErrNow = 1.0 for new agents, indicating that they correctly perceive their productivity.

        Parameters
        ----------
        which_agents : np.array(Bool)
            Boolean array of size self.AgentCount indicating which agents should be "born".

        Returns
        -------
        None
        '''
        AggShockConsumerType.simBirth(self,which_agents)
        if hasattr(self,'pLvlErrNow'):
            self.pLvlErrNow[which_agents] = 1.0
        else: # This only triggers at the beginning of the very first simulated period
            self.pLvlErrNow = np.ones(self.AgentCount)
            self.t_since_update = np.zeros(self.AgentCount,dtype=int)
            

    def getUpdaters(self):
        '''
        Determine which agents update this period vs which don't.  Fills in the
        attributes update and dont as boolean arrays of size AgentCount.  Also
        updates the attribute t_since_update, incrementing it for non-updaters
        and setting it to zero for updaters.
        
        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        # Increment the periods-since-updated counter for each agent
        self.t_since_update += 1
        
        # Initialize the random draw of Pi*N agents who update
        how_many_update = int(round(self.UpdatePrb*self.AgentCount))
        base_bool = np.zeros(self.AgentCount,dtype=bool)
        base_bool[0:how_many_update] = True
        
        # Update if touched by the Calvo fairy, or its been too long since the last update
        self.update = self.RNG.permutation(base_bool)
        if (self.max_t_between_updates is not None) and (self.UpdatePrb < 1.0):
            too_long_since_update = self.t_since_update >= self.max_t_between_updates
            self.update[too_long_since_update] = True
        
        # Mark non-updaters as the complementary set, and reset the time since
        # update counter for updaters
        self.dont = np.logical_not(self.update)
        self.t_since_update[self.update] = 0

        
    def getpLvlError(self):
        '''
        Calculates and returns the misperception of this period's shocks.  Updaters
        have no misperception this period, while those who don't update don't see
        the value of the aggregate permanent shock and assume aggregate growth
        equals its expectation.


        Parameters
        ----------
        None

        Returns
        -------
        pLvlErr : np.array
            Array of size AgentCount with this period's (new) misperception.
        '''
        pLvlErr = np.ones(self.AgentCount)
        pLvlErr[self.dont] = self.PermShkAggNow/self.PermGroFacAgg
        return pLvlErr


    def getShocks(self):
        '''
        Gets permanent and transitory shocks (combining idiosyncratic and aggregate shocks), but
        only consumers who update their macroeconomic beliefs this period incorporate all pre-
        viously unnoticed aggregate permanent shocks.  Agents correctly observe the level of all
        real variables (market resources, consumption, assets, etc), but misperceive the aggregate
        productivity level.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        # The strange syntax here is so that both StickyEconsumerType and StickyEmarkovConsumerType
        # run the getShocks method of their first superclass: AggShockConsumerType and
        # AggShockMarkovConsumerType respectively.  This will be simplified in Python 3.
        super(self.__class__,self).getShocks() # Get permanent and transitory combined shocks
        newborns = self.t_age == 0
        self.TranShkNow[newborns] = self.TranShkAggNow*self.wRteNow # Turn off idiosyncratic shocks for newborns
        self.PermShkNow[newborns] = self.PermShkAggNow
        self.getUpdaters() # Randomly draw which agents will update their beliefs

        # Calculate innovation to the productivity level perception error
        pLvlErrNew = self.getpLvlError()
        self.pLvlErrNow *= pLvlErrNew # Perception error accumulation

        # Calculate (mis)perceptions of the permanent shock
        PermShkPcvd = self.PermShkNow/pLvlErrNew
        PermShkPcvd[self.update] *= self.pLvlErrNow[self.update] # Updaters see the true permanent shock and all missed news
        self.pLvlErrNow[self.update] = 1.0
        self.PermShkNow = PermShkPcvd
        
        # The block of code below will only ever activate during an experiment about the MPC
        # from the arrival of a transitory shock that can be foreseen and borrowed against
        # by individuals who update.  The results of this experiment do not appear in the
        # main text of the paper.
        if not hasattr(self,'parker_experiment'): # This attribute is added for an experiment
            return
        if not hasattr(self,'noticed'): # If the "noticed" attribute does not exist, initialize it
            self.noticed = np.zeros(self.AgentCount,dtype=bool)
        if self.BonusLvl > 0.:
            if self.t_until_bonus > 0: # Which agents "notice" the future bonus this period
                noticers = np.logical_and(self.update, np.logical_not(self.noticed)) 
            else: # Everyone notices when bonus check actually arrives
                noticers = np.logical_not(self.noticed) 
            BonusNrm = np.zeros_like(self.TranShkNow)
            BonusNrm[noticers] = self.BonusLvl/(self.pLvlNow[noticers]*self.PermShkNow[noticers])
            self.TranShkNow += BonusNrm*self.getRfree()**(-self.t_until_bonus)
            # Agents who notice the check perceive it as a transitory shock to their income,
            # normalized by their perception of their permanent income and discounted by
            # the interest factor T periods ahead.
            self.noticed[noticers] = True
            self.t_until_bonus -= 1 # Bonus check arrival is one period closer
        

    def getStates(self):
        '''
        Gets simulated consumers pLvl and mNrm for this period, but with the alteration that these
        represent perceived rather than actual values.  Also calculates mLvlTrue, the true level of
        market resources that the individual has on hand.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        # Update consumers' perception of their permanent income level
        pLvlPrev = self.pLvlNow
        self.pLvlNow = pLvlPrev*self.PermShkNow # Perceived permanent income level (only correct if macro state is observed this period)
        self.PlvlAggNow *= self.PermShkAggNow # Updated aggregate permanent productivity level
        self.pLvlTrue = self.pLvlNow*self.pLvlErrNow

        # Calculate what the consumers perceive their normalized market resources to be
        RfreeNow = self.getRfree()
        bLvlNow = RfreeNow*self.aLvlNow # This is the true level

        yLvlNow = self.pLvlTrue*self.TranShkNow # This is true income level
        mLvlTrueNow = bLvlNow + yLvlNow # This is true market resource level
        mNrmPcvdNow = mLvlTrueNow/self.pLvlNow # This is perceived normalized resources
        self.mNrmNow = mNrmPcvdNow
        self.mLvlTrueNow = mLvlTrueNow
        self.yLvlNow = yLvlNow # Only labor income


    def getMaggNow(self):
        '''
        Gets each consumer's perception of normalized aggregate market resources.
        Very simple overwrite of method from superclass.

        Parameters
        ----------
        None

        Returns
        -------
        MaggPcvdNow : np.array
            1D array of perceived normalized aggregate market resources.
        '''
        MaggPcvdNow = self.MaggNow*self.pLvlErrNow  # Agents know the true level of aggregate market resources,
        return MaggPcvdNow # but have erroneous perception of pLvlAgg.


    def getPostStates(self):
        '''
        Slightly extends the base version of this method by recalculating aLvlNow to account for the
        consumer's (potential) misperception about their productivity level.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        AggShockConsumerType.getPostStates(self)
        self.cLvlNow = self.cNrmNow*self.pLvlNow # True consumption level
        self.aLvlNow = self.mLvlTrueNow - self.cLvlNow # True asset level
        self.aNrmNow = self.aLvlNow/self.pLvlNow # Perceived normalized assets


class StickyEmarkovConsumerType(AggShockMarkovConsumerType,StickyEconsumerType):
    '''
    A class for representing consumers who have sticky expectations about the macroeconomy
    because they do not observe aggregate variables every period.  This version lives
    in an economy subject to Markov shocks to the aggregate income process.  Agents don't
    necessarily update their perception of the aggregate productivity level or the discrete
    Markov state (governing aggregate growth) in every period.  Most of its methods are
    directly inherited from one of its parent classes.
    '''
    def simBirth(self,which_agents): # Inherit from StickyE rather than AggShock
        StickyEconsumerType.simBirth(self,which_agents)

    def getShocks(self): # Inherit from StickyE rather than AggShock
        StickyEconsumerType.getShocks(self)

    def getStates(self): # Inherit from StickyE rather than AggShock
        StickyEconsumerType.getStates(self)

    def getPostStates(self): # Inherit from StickyE rather than AggShock
        StickyEconsumerType.getPostStates(self)

    def getMaggNow(self): # Inherit from StickyE rather than AggShock
        return StickyEconsumerType.getMaggNow(self)

    def getMrkvNow(self): # Agents choose control based on *perceived* Markov state
        return self.MrkvNowPcvd


    def getUpdaters(self):
        '''
        Determine which agents update this period vs which don't.  Fills in the
        attributes update and dont as boolean arrays of size AgentCount.  This
        version also updates perceptions of the Markov state.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        StickyEconsumerType.getUpdaters(self)
        # Only updaters change their perception of the Markov state
        if hasattr(self,'MrkvNowPcvd'):
            self.MrkvNowPcvd[self.update] = self.MrkvNow
        else: # This only triggers in the first simulated period
            self.MrkvNowPcvd = np.ones(self.AgentCount,dtype=int)*self.MrkvNow


    def getpLvlError(self):
        '''
        Calculates and returns the misperception of this period's shocks.  Updaters
        have no misperception this period, while those who don't update don't see
        the value of the aggregate permanent shock and thus base their belief about
        aggregate growth on the last Markov state that they actually observed,
        which is stored in MrkvNowPcvd.

        Parameters
        ----------
        None

        Returns
        -------
        pLvlErr : np.array
            Array of size AgentCount with this period's (new) misperception.
        '''
        pLvlErr = np.ones(self.AgentCount)
        pLvlErr[self.dont] = self.PermShkAggNow/self.PermGroFacAgg[self.MrkvNowPcvd[self.dont]]
        return pLvlErr
    
    
    def installAltShockBeliefs(self):
        '''
        Makes this agent type believe that aggregate permanent shocks only arrive
        at all with UpdatePrb probability-- that their sticky expectations are the
        true aggregate shock process.  Puts the attribute PermShkAggDstnAlt into
        the attribute IncomeDstn and swaps MrkvArray for MrkvArrayAlt.
        
        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        if not hasattr(self,'beliefs_alt'):
            self.beliefs_alt = False # Initialize alternate beliefs flag
            
        if not self.beliefs_alt:
            self.MrkvArray_orig = deepcopy(self.MrkvArray)
            self.IncomeDstn_orig = deepcopy(self.IncomeDstn)
            self.MrkvArray = self.MrkvArrayAlt
            self.addAggShkDstn(self.AggShkDstnAlt)
            self.beliefs_alt = True # Set alternate beliefs flag
            
            
    def resetShockBeliefs(self):
        '''
        Returns this agent type's attributes to the standard values, undoing the
        the swaps in installAltShockBeliefs().  This should be called before
        simulating the model.
        
        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        if not hasattr(self,'beliefs_alt'):
            self.beliefs_alt = False # Initialize alternate beliefs flag
            
        if self.beliefs_alt: # This only actually does something if installAltShockBeliefs() has been run
            self.MrkvArray = self.MrkvArray_orig
            self.IncomeDstn = self.IncomeDstn_orig
            self.beliefs_alt = False # Set alternate beliefs flag



class StickyErepAgent(RepAgentConsumerType):
    '''
    A representative consumer who has sticky expectations about the macroeconomy because
    he does not observe aggregate variables every period.  Agent lives in a Cobb-Douglas economy.
    '''
    def simBirth(self,which_agents):
        '''
        Makes new consumers for the given indices.  Slightly extends base method by also setting
        pLvlTrue = 1.0 in the very first simulated period.

        Parameters
        ----------
        which_agents : np.array(Bool)
            Boolean array of size self.AgentCount indicating which agents should be "born".

        Returns
        -------
        None
        '''
        super(self.__class__,self).simBirth(which_agents)
        if self.t_sim == 0: # Make sure that pLvlTrue and aLvlNow exist
            self.pLvlTrue = np.ones(self.AgentCount)
            self.aLvlNow = self.aNrmNow*self.pLvlTrue


    def getShocks(self):
        super(self.__class__,self).getShocks() # Get actual permanent and transitory shocks


    def getStates(self):
        '''
        Calculates updated values of normalized market resources and permanent income level.
        Makes both perceived and true values.  The representative consumer will act on the
        basis of his *perceived* normalized market resources.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        # Calculate perceived and true productivity level
        aLvlPrev = self.aLvlNow
        self.pLvlTrue = self.pLvlTrue*self.PermShkNow
        self.pLvlNow = self.getpLvlPcvd()

        # Calculate true values of variables
        self.kNrmTrue = aLvlPrev/self.pLvlTrue
        self.yNrmTrue = self.kNrmTrue**self.CapShare*self.TranShkNow**(1.-self.CapShare) - self.kNrmTrue*self.DeprFac
        self.Rfree = 1. + self.CapShare*self.kNrmTrue**(self.CapShare-1.)*self.TranShkNow**(1.-self.CapShare) - self.DeprFac
        self.wRte  = (1.-self.CapShare)*self.kNrmTrue**self.CapShare*self.TranShkNow**(-self.CapShare)
        self.mNrmTrue = self.Rfree*self.kNrmTrue + self.wRte*self.TranShkNow
        self.mLvlTrue = self.mNrmTrue*self.pLvlTrue

        # Calculate perception of normalized market resources
        self.mNrmNow = self.mLvlTrue/self.pLvlNow


    def getControls(self):
        super(self.__class__,self).getControls()
        self.cLvlNow = self.cNrmNow*self.pLvlNow # This is true


    def getPostStates(self):
        '''
        Slightly extends the base version of this method by recalculating aLvlNow to account for the
        consumer's (potential) misperception about their productivity level.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        RepAgentConsumerType.getPostStates(self)
        self.aLvlNow = self.mLvlTrue - self.cLvlNow # This is true
        self.aNrmNow = self.aLvlNow/self.pLvlTrue # This is true

    def getpLvlPcvd(self):
        '''
        Finds the representative agent's (average) perceived productivity level.
        Average perception of productivity gets UpdatePrb weight on the true level,
        for those that update, and (1-UpdatePrb) weight on the previous average
        perception times expected aggregate growth, for those that don't update.

        Parameters
        ----------
        None

        Returns
        -------
        pLvlPcvd : np.array
            Size 1 array with average perception of productivity level.
        '''
        pLvlPcvd = self.UpdatePrb*self.pLvlTrue + (1.0-self.UpdatePrb)*(self.pLvlNow*self.PermGroFac[self.t_cycle[0]-1])
        return pLvlPcvd


class StickyEmarkovRepAgent(RepAgentMarkovConsumerType,StickyErepAgent):
    '''
    A representative consumer who has sticky expectations about the macroeconomy because
    he does not observe aggregate variables every period.  Agent lives in a Cobb-Douglas
    economy that has a discrete Markov state.  If UpdatePrb < 1, the representative agent's
    perception of the Markov state is distributed across the previous states visited.
    '''
    def simBirth(self,which_agents):
        '''
        Makes new consumers for the given indices.  Slightly extends base method by also setting
        pLvlTrue = 1.0 in the very first simulated period, as well as initializing the perception
        of aggregate productivity for each Markov state.  The representative agent begins with
        the correct perception of the Markov state.

        Parameters
        ----------
        which_agents : np.array(Bool)
            Boolean array of size self.AgentCount indicating which agents should be "born".

        Returns
        -------
        None
        '''
        if which_agents==np.array([True]):
            RepAgentMarkovConsumerType.simBirth(self,which_agents)
            if self.t_sim == 0: # Initialize perception distribution for Markov state
                self.pLvlTrue = np.ones(self.AgentCount)
                self.aLvlNow = self.aNrmNow*self.pLvlTrue
                StateCount = self.MrkvArray.shape[0]
                self.pLvlNow = np.ones(StateCount) # Perceived productivity level by Markov state
                self.MrkvPcvd = np.zeros(StateCount) # Distribution of perceived Markov state
                self.MrkvPcvd[self.MrkvNow[0]] = 1.0 # Correct perception of state initially


    def getShocks(self): # Inherit from StickyE rather than RepresentativeAgent
        StickyErepAgent.getShocks(self)

    def getStates(self): # Inherit from StickyE rather than RepresentativeAgent
        StickyErepAgent.getStates(self)

    def getPostStates(self): # Inherit from StickyE rather than RepresentativeAgent
        StickyErepAgent.getPostStates(self)


    def getpLvlPcvd(self):
        '''
        Finds the representative agent's (average) perceived productivity level
        for each Markov state, as well as the distribution of the representative
        agent's perception of the Markov state.

        Parameters
        ----------
        None

        Returns
        -------
        pLvlPcvd : np.array
            Array with average perception of productivity level by Markov state.
        '''
        StateCount = self.MrkvArray.shape[0]
        t = self.t_cycle[0]
        i = self.MrkvNow[0]

        dont_mass = self.MrkvPcvd*(1.-self.UpdatePrb) # pmf of non-updaters
        update_mass = np.zeros(StateCount)
        update_mass[i] = self.UpdatePrb # pmf of updaters

        dont_pLvlPcvd = self.pLvlNow*self.PermGroFac[t-1] # those that don't update think pLvl grows at PermGroFac for last observed state
        update_pLvlPcvd = np.zeros(StateCount)
        update_pLvlPcvd[i] = self.pLvlTrue # those that update see the true pLvl

        # Combine updaters and non-updaters to get average pLvl perception by Markov state
        self.MrkvPcvd = dont_mass + update_mass # Total mass of agent in each state
        pLvlPcvd = (dont_mass*dont_pLvlPcvd + update_mass*update_pLvlPcvd)/self.MrkvPcvd
        pLvlPcvd[self.MrkvPcvd==0.] = 1.0 # Fix division by zero problem when MrkvPcvd[i]=0
        return pLvlPcvd


    def getControls(self):
        '''
        Calculates consumption for the representative agent using the consumption functions.
        Takes the weighted average of cLvl across perceived Markov states.

        Parameters
        ----------
        None

        Returns
        -------
        None
        '''
        StateCount = self.MrkvArray.shape[0]
        t = self.t_cycle[0]

        cNrmNow = np.zeros(StateCount) # Array of chosen cNrm by Markov state
        for i in range(StateCount):
            cNrmNow[i] = self.solution[t].cFunc[i](self.mNrmNow[i])
        self.cNrmNow = cNrmNow
        self.cLvlNow = np.dot(cNrmNow*self.pLvlNow,self.MrkvPcvd) # Take average of cLvl across states


class StickyCobbDouglasEconomy(CobbDouglasEconomy):
    '''
    This is almost identical to CobbDouglasEconomy, except it overrides the mill
    rule to use pLvlTrue instead of pLvlNow
    '''
    def __init__(self,agents=[],tolerance=0.0001,act_T=1000,**kwds):
        '''
        Make a new instance of StickyCobbDouglasEconomy by filling in attributes
        specific to this kind of market.

        Parameters
        ----------
        agents : [ConsumerType]
            List of types of consumers that live in this economy.
        tolerance: float
            Minimum acceptable distance between "dynamic rules" to consider the
            solution process converged.  Distance depends on intercept and slope
            of the log-linear "next capital ratio" function.
        act_T : int
            Number of periods to simulate when making a history of of the market.

        Returns
        -------
        None
        '''
        CobbDouglasEconomy.__init__(self,agents=agents,tolerance=tolerance,act_T=act_T,**kwds)
        self.reap_vars = ['aLvlNow','pLvlTrue']

    def millRule(self,aLvlNow,pLvlTrue):
        '''
        Function to calculate the capital to labor ratio, interest factor, and
        wage rate based on each agent's current state.  Just calls calcRandW().

        See documentation for calcRandW for more information.
        '''
        return self.calcRandW(aLvlNow,pLvlTrue)



class StickyCobbDouglasMarkovEconomy(CobbDouglasMarkovEconomy):
    '''
    This is almost identical to CobbDouglasmarkovEconomy, except it overrides the
    mill rule to use pLvlTrue instead of pLvlNow.
    '''
    def __init__(self,agents=[],tolerance=0.0001,act_T=1000,**kwds):
        '''
        Make a new instance of StickyCobbDouglasMarkovEconomy by filling in attributes
        specific to this kind of market.

        Parameters
        ----------
        agents : [ConsumerType]
            List of types of consumers that live in this economy.
        tolerance: float
            Minimum acceptable distance between "dynamic rules" to consider the
            solution process converged.  Distance depends on intercept and slope
            of the log-linear "next capital ratio" function.
        act_T : int
            Number of periods to simulate when making a history of of the market.

        Returns
        -------
        None
        '''
        CobbDouglasMarkovEconomy.__init__(self,agents=agents,tolerance=tolerance,act_T=act_T,**kwds)
        self.reap_vars = ['aLvlNow','pLvlTrue']

    def millRule(self,aLvlNow,pLvlTrue):
        '''
        Function to calculate the capital to labor ratio, interest factor, and
        wage rate based on each agent's current state.  Just calls calcRandW()
        and adds the Markov state index.

        See documentation for calcRandW for more information.
        '''
        MrkvNow = self.MrkvNow_hist[self.Shk_idx]
        temp =  self.calcRandW(aLvlNow,pLvlTrue)
        temp(MrkvNow = MrkvNow)

        # Overwrite MaggNow, wRteNow, and RfreeNow if requested
        if self.overwrite_hist:
            t = self.Shk_idx-1
            temp(MaggNow = self.MaggNow_overwrite[t])
            temp(wRteNow = self.wRteNow_overwrite[t])
            temp(RfreeNow = self.RfreeNow_overwrite[t])

        return temp
    
    
class StickySmallOpenMarkovEconomy(SmallOpenMarkovEconomy):  
    '''
    This is identical to the class SmallOpenMarkovEconomy from ConsAggShockModel,
    but it adds one method that is only used for an experiment that is not reported
    in the main text of the paper.
    '''
    
    def runParkerExperiment(self,T_sim):
        '''
        Simulates T_sim periods of the "Parker experiment", in which a "bonus check"
        is announced to households in advance of it actually arriving, but only
        households who update to the latest macroeconomic news "notice" the future
        arrival of the bonus.  Households who "notice" the bonus in advance may
        borrow against it to finance consumption, and thus perceive it as a discounted
        transitory shock to income.  Households who don't notice the announcement
        will see it when it actually arrives in their bank account.
        
        Parameters
        ----------
        T_sim : int
            Number of periods to simulate.
            
        Returns
        -------
        cLvlMean_hist : np.array
            Array of size T_sim with population average consumption for each simulated period.
        '''
        cLvlMean_hist = np.zeros(T_sim) + np.nan
        
        for t in range(T_sim):
            self.sow()       # Distribute aggregated information/state to agents
            self.cultivate() # Agents take action
            self.reap()      # Collect individual data from agents
            self.mill()      # Process individual data into aggregate data
            cLvl_new = np.concatenate([self.agents[i].cLvlNow for i in range(len(self.agents))])
            cLvlMean_hist[t] = np.mean(cLvl_new)
        
        return cLvlMean_hist
            
