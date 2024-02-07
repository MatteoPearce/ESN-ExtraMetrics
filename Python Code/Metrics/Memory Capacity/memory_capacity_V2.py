# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 15:15:04 2023

@author: mp1432
"""

"""
derived from calc sent by Chester Wringe, intended for use with GenDataset_V7.
receives:
    
    model        --> reservoirpy.model, needs to have a ridge node as output
    input_stream --> numpy ndarray of shape (x,1)
    nc           --> number of neurons in reservoirpy.Reservoir node
    order        --> order
"""

from reservoirpy import model
from numpy import zeros, ndarray
from scipy.special import binom

#-----------------------------------------------------------------------------#

def MC_n(model: model, 
         input_stream: ndarray, 
         nc: int, 
         order : int = 1) -> float:
    
    n = len(input_stream)
    testing = False
 
# TRAIN ESN #

    # chose the simplest training task to implement: 1 timestep prediction
    # of randomly generated sequence of numbers.

    m = int( n / 2 )

    X_train = input_stream[0:m]
    Y_train = input_stream[1:m+1]
    assert len(X_train) == len(Y_train)

    model = model.fit(X_train, Y_train, warmup=0) #training step
    Y_pred = model.run(input_stream[m:]) #observed trained output
    future = zeros([Y_pred.shape[0]]) # v(t + i) 

# CALC FUTURE #

    first_term = 1 / ( 2**order )
    sum_term = 0
    
    # future array is same length as the training set, and each list element is 
    # updated singularly, as many times per element as is equal to the order. 
    
    for i in range(m): # for each element up to m in list of inputs
        for j in range(order): # for each summation term (see n^th deg memory capacity formula)
            binomial_term = binom(order,j) ** 2 # scipy.special function, returns result of binomial
            first_term = (input_stream[i] - 1) ** (order - j) # (u(t) - 1)^(n-k)
            second_term = (input_stream[i] + 1) ** j # (u(t) + 1) ^ k
            sum_term = first_term * binomial_term * first_term * second_term
            future[i] = future[i] + sum_term #update each list element as many times as order
    
    if testing:
        assert len(future) == len(Y_pred)

# CALC MSE #
            
    sum_term = 0
    
    for i in range(nc):
        sum_term = sum_term + ( future[i] - Y_pred[i] ) ** 2
    
    MSE = sum_term / m
    y_pred_mean = Y_pred / m
    
    for i in range(m):
        sum_term = sum_term + ( future[i] - y_pred_mean[i] ) ** 2
    
    MSE_av = sum_term / m
    
# CALC NMSE #

    NMSE = MSE / MSE_av
    
    return NMSE[0]






