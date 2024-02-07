# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 16:08:47 2023

@author: mp1432
"""
"""
This class is for quick creation of reservoirpy models. it iniliasises with a set
of default values as defined by the literature for ESNs. allows for creation of more
than 1 model per call, as well as allowing for 4 differing interconnections between
nodes. To create multiple identical models, set nn to the desired number; for different
models, set nn to 1 and repeat calls to ESN_Maker, passing desired parameters.
"""

import reservoirpy as res
from reservoirpy.nodes import Reservoir, Input, Output
from reservoirpy.mat_gen import random_sparse
from dataclasses import dataclass, field
import numpy as np

@dataclass
class ESN_Maker ():   
    
    config_params: list # configuration parameters 
    res_params: list # Reservoir parameters
    networks: list[res.model] = field(default_factory=[]) # list of all created models
    
#----------------------------------INIT---------------------------------------#
       
    def __init__(
                 self,  
                 
                 # configuration parameters
                 
                 nn : int = 1, #network count
                 cn : str = 'simple', #config type. see class description ^^^
                 init: bool = True, # if True, model.call() of 1 timestep of random data
                 init_W: str = None, # if a valid name, initialise reservoir W matrix
                 out: bool = True, # if True, create output node
                 
                 # reservoirpy.Reservoir parameters:
                 
                 nc : int = None, #node count
                 lr: float = 0.1, #leak rate: recall of previous states
                 sr: float = 1.0, # spectral radius: max egeinvalue in W, close to 1 for ESP
                 cny: float = 0.1, #connectivity: low for ESP
                 ins: float = 1.0, # input scaling 
                 ins_cny: float = 0.1, #input connectivity: low for ESP
                         
                 # other
                 
                 verb: bool = False, # sets verbosity
                 rep: bool = False, # sets reproducibility
                 seed: int = 42
                ):
        
                    if nc == None:
                        raise ValueError("You haven't told me how many nodes you want.")
                    elif nn < 1:
                        raise ValueError("You can't request less than 1 ESN.")
                    elif nn > 10:
                        raise ValueError("You can't request more than 10 ESNs")
                        
                    self.res_params = [nc,lr,sr,cny,ins,ins_cny]
                    self.config_params = [nn,cn.lower(),init,init_W,out]
                    
                    self.make_nodes(nn, cn.lower(), out)
                    self.init_network(init, init_W)
                    self.set_others(verb,rep,seed)
                    
#-------------INSTANTIATE RESERVOIRPY NODES AND CREATE MODEL------------------#
      
    # class field res_params is used to set all the desired reservoir parameters.
              
    def make_nodes(self,nn,cn,out):
        
        self.networks = []
        for i in range(nn):
            
            an_input = Input()
            an_output = Output()
            an_reservoir = Reservoir(units=self.res_params[0],
                                     lr=self.res_params[1],
                                     sr=self.res_params[2],
                                     rc_connectivity=self.res_params[3],
                                     input_scaling=self.res_params[4],
                                     input_connectivity=self.res_params[5]
                                     )
        
            if cn == 'simple':
               if out:
                   model = an_input >> an_reservoir >> an_output
               else:
                   model = an_input >>an_reservoir
                    
            elif cn == 'parallel': 
                model = [an_input, an_input >> an_reservoir] >> an_output
                    
            elif cn == 'feedback':
                an_reservoir <<= an_output
                model = an_input >> an_reservoir >> an_output
            
            elif cn == 'complex':
                an_reservoir <<= an_output
                model = [an_input, an_input >> an_reservoir] >> an_output
            
            else:
                raise ValueError("you have misspelt your connection type. options are: \n \
                                  simple: input -> reservoir -> output \n \
                                  parallel: [input -> reservoir] -> output \n \
                                  feedback: input -> reservoir -> output -> reservoir \n \
                                  complex: [input -> reservoir] -> output -> reservoir \
                                 ")
            
            self.networks.append(model)
            
#-------------------------INITIALISE MODEL NODES------------------------------#
    
    def init_network(self,init,init_W):
        
        if init:
            init_data = np.random.random([1,1])
            for esn in self.networks:
                esn.run(init_data)
        
        if init_W is not None:
            
            try:
                initializer = random_sparse(
                                            dist=init_W,
                                            loc = -1, # for range [-1:1] 
                                            scale = 2,  # for range [-1:1]
                                            input_scaling = 0.5 # for range [-0.5:0.5]
                                           )
                
                init_res = initializer(self.res_params[0], # reservoir matrix weights
                                       self.res_params[0]) # needs to be saved to variable first, otherwise will differ.
                
                init_win = initializer(self.res_params[0],1) # matrix input weights

                for network in self.networks:
                    network.nodes[1].W = init_res # node 1 is always reservoir when using ESN_Maker
                    network.nodes[1].Win = init_win
                    
            except:
                print("invalid distribution")
                
#-----------------------------SET REPRODUCIBILITY-----------------------------#
    
    def set_others(self,verb,rep,seed):
        
        if not verb:
            res.verbosity(0)  # reduces number of printouts
        
        if rep:
            res.set_seed(seed)  # make everything reproducible
            
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    