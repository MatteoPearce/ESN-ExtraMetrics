# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 15:04:45 2023

@author: mp1432
"""

""" 
function for calculating the shannon entropy of the output matrix of an ESN.
intended for use with GetDataset_V7.
receives:
    
    model          --> reservoirpy.model, needs to have a ridge node as output
    input_stream   --> numpy ndarray of shape (x,1)
    columnwise     --> boolean, if true output matrix columns are concatenated. if false, rows.
    history length --> number of output matrix elements to consider as history when determining events
    bucket_count   --> inverse of size of event thresholds. example: bucket_count = 10 -> event thresholds are 0.1 wide.
    
"""

import numpy as np
from scipy.stats import entropy
from itertools import product
from reservoirpy import model

def Shannon_Entropy (model: model = None,
                     input_stream: np.ndarray = None,
                     columnwise : bool = False, 
                     history_length : int = 2,
                     bucket_count: int = 10):
    
#----------------#GENERATE INPUT STREAM AND OUTPUT MATRIX#--------------------#
    
    if input_stream is None: # create random input stream if none provided
        # get reservoir neuron count:
        res_name = model.node_names 
        for name in res_name:
            if any(x == 'R' for x in name):
                res_name = name
                break
        stream_length = model.get_node(f"{res_name}").get_param("units") * 4                   
        input_stream = np.random.random([stream_length,1]) - 0.5 # input range [-0.5:0.5]
        
    output_matrix = np.zeros([input_stream.shape[0], 
                              model.nodes[-1].output_dim]) # matrix of zeros, of size (input length, neurons)
    
    for index, data in enumerate(input_stream): # initialise reservoir with 1 input datapoint
        output_matrix[index] = model.call(data)[0] # creates row of the output of n output nodes.
   
#------------#RESHAPE MATRIX, PLACE ELEMENTS IN EVENT INTERVALS#--------------#
        
    if columnwise:
        output_matrix = ( np.reshape(output_matrix,(1,-1),'F')[0]) #concatenates columns  
    else:
        output_matrix = ( np.reshape(output_matrix,(1,-1),)[0]) #concatenates rows 

    output_matrix = (output_matrix - output_matrix.min()) / (output_matrix.max() - output_matrix.min() + 1e-16) # scale

    for index, value in enumerate(output_matrix):          
        output_matrix[index] = int(value * bucket_count) + 1 # replace matrix element with number of bucket within which it falls
        
        if output_matrix[index] == bucket_count + 1: # avoids elements exactly equal to upper threshold of final bucket generating error
            output_matrix[index] = bucket_count
        
#------------------------#GENERATE POSSIBLE EVENTS#---------------------------#

    buckets = np.arange(1,bucket_count+1) # numbers each bucket
    
    possible_events = list(product(buckets,repeat=(history_length+1))) # itertools.permutations does not allow repititions
    possible_events = list(np.unique(possible_events,axis=0)) # remove repeated events

    event_index = {tuple(y): x for x, y in enumerate(possible_events)} # create dict with all possible events for rapid lookup
    
#-------------------------#COUNT EVENT OCCURENCES#----------------------------#

    scrolling_window = []
    occurences = [0] * len(possible_events) # list for counting event occurences, begins as list of zeros

    for index, value in enumerate(output_matrix):  

            scrolling_window.append(value)
            
            if len(scrolling_window) > history_length + 1: 
                scrolling_window.pop(0)
            
            if len(scrolling_window) == history_length + 1: # history 1, history 2, current
                occurences[event_index[tuple(scrolling_window)]] += 1 #check event index for occurence, if true return index, increment occurences
                 
                 
#------------------#ADD NO HISTORY EVENTS AND OCCURENCES#---------------------#

    """ 
    for a set of symbols, a number of extra states arise from the addition of a
    "no history" prefix - a fourth symbol, which cannot however appear in all 
    possible positions in the sequence. the only events observed with no history
    are those where scrolling_window has a length less than history_length + 1. 
    for example:
        
        events = a b c
        history length = 2
        
    the first value appended to scrolling_window can only be either a, b or c.
    so we get 1 observed event with no history, with 3 possible events.
    
    the second value appended to scrolling_window can again only be either 
    a, b or c, meaning that we get 1 observed event with partial history, from a
    possible 9 events. 
    
    therefore, we always observe a number of no history events equal to
    history length, from a number of possible events equal to:
        
        r = symbols
        extra possible events = r^1 + r^2 ..... r^(history_length)
    
    so in this example we get an extra r^1 + r^2 = 3 + 9 = 12 events. 
    
    the position of where these occurences and possible events are stored in the
    occurences list doesn't influence the entropy calculation, so they are appended
    after all the scrolling_window loops for simpliocity. This is what the 
    following block is doing:
        """

    for i in range(1,history_length+1,1):
        occurences.append(1)
        states = (bucket_count) ** i
        for j in range(states):
            occurences.append(0)

#--------------------------#ENTROPY CALCULATION#------------------------------#

    for i in range(len(occurences)):
        if occurences[i] == 0:
            occurences[i] = 1e-10
    
    H = entropy(occurences,base=len(occurences)) # from scipy.stats
    
    return H        







