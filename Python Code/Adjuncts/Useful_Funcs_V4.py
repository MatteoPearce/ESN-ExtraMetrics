# -*- coding: utf-8 -*-
"""
Created on Thu Jul 20 15:20:25 2023

@author: mp1432
"""

""" 
    random collection of useful functions, to tidy up scripts.
    
    ParaMake --> creates as many newlines as requested.
    SepaMake --> prints as many lines of dashes as requested, to create separation.
    Sect_Div --> Section Divider, 2 ParaMake + 2 SepaMake + 2 ParaMake.
    PrintMatrix --> receives numpy.ndarray and prints in more legible format.
    
    Mean_El_Var --> receives two arrays, computes mean distance between each datapoint
                    of equal index.
    Val_Spread --> receives matrix and computes max, min & spread: returns list.
"""


#-----------------------------------------------------------------------------#   
#-----------------------------------------------------------------------------#
    
def ParaMake (paranum : int = None):
    
    if paranum == None:
        paranum = 2
    
    for i in range(paranum):
        print()
        
#-----------------------------------------------------------------------------#   
#-----------------------------------------------------------------------------#  
        
def SepaMake (sepanum : int = 1):
    
    for i in range(sepanum):
        print("---------------------------------------------------------------------------")
 
#-----------------------------------------------------------------------------#   
#-----------------------------------------------------------------------------# 
        
def Sect_Div ():
    
    ParaMake(2)
    SepaMake(2)
    ParaMake(2)
    
#-----------------------------------------------------------------------------#   
#-----------------------------------------------------------------------------#     
        
from numpy import ndarray

def PrintMatrix (matrix: ndarray, matrix_name: str = None):
    
    if matrix_name != None: 
    
        print(matrix_name + "\n")
    
    else:
        print("MATRIX START \n")
    
    for i in range( len(matrix) ):

        print(matrix[i])

    print("\nMATRIX END")

#-----------------------------------------------------------------------------#   
#-----------------------------------------------------------------------------# 

def Mean_El_Var(matrix_1,matrix_2) -> float:
    
    for row in matrix_1:
        for i in range(len(row)):
            if row[i] == 0.0000:
                row[i] = 0.0001

    for row in matrix_2:
        for i in range(len(row)):
            if row[i] == 0.0000:
                row[i] = 0.0001               

    check = []
    check.append( abs(matrix_1 - matrix_2) )
                
    sumterm = 0
    count = 0

    ParaMake(2)

    for row in check[0]:
        for i in range(len(row)):
            if row[i] > 1:
                row[i] = row[i]**(-1)
                
            sumterm = sumterm + row[i]
            count += 1
    average_var = sumterm / count 
   
    return average_var

#-----------------------------------------------------------------------------#   
#-----------------------------------------------------------------------------# 

def Val_Spread (matrix) -> list:
    
    biggest = matrix.max()
    smallest = matrix.min()
    spread = biggest - smallest

    return [biggest,smallest,spread]

#-----------------------------------------------------------------------------#   
#-----------------------------------------------------------------------------#




