# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 14:32:56 2023

@author: mp1432
"""

"""
script for generating datasets whilst sweeping up to 2 ESN parameters. compatible with 
any metric function with header line of following structure:
    
     a function (
                 model: reservoirpy.model
                 input_stream: numpy.ndarray
                 calc_specific_paramter_1 : any
                 calc_specific_paramter_2 : any
                 .
                 .
                 calc_specific_paramter_N : any
                )
     
or:
    a function (
                model: reservoirpy.model
                calc_specific_paramter_1 : any
                calc_specific_paramter_2 : any
                .
                .
                calc_specific_paramter_N : any
               )
    
     
receives:
    
    datasets        --> how many .txt files of the same sweep to generate, each with different seed
    dir_path        --> directory of where to save .txt files
    double_sweep    --> give True if sweeping two parameters
    training        --> if True, add ridge output node to model
    gen_input       --> if true, generate randomised input datastream
    target_function --> tuple of 2 strings: function name and path to its .py
    parameters      --> dictionary of parameters to sweep. names are keys, values tuple of (start,stop,step)
    function_params --> variables specific and required for the calculation of metric. 
    model_list      --> use only if you have a list of reservoirpy.model for specific ESNs.
    keep_buildpath  --> if true, the directory used for build steps of .txt files won't be discarded
    
    
"""

import numpy as np
from itertools import product
from reservoirpy import model
from reservoirpy.nodes import Ridge
from random import randint
from os import path, mkdir, listdir
from typing import Union
import importlib.util
import sys
from inspect import getmembers, isfunction
import json
import shutil
import string

def GetDataset   (datasets: int = 1, 
                  dir_path: str = None,
                  double_sweep: bool = False,
                  training: bool = False,
                  gen_input: bool = False,
                  target_function: tuple((str,str)) = None,
                  parameters: dict = None,
                  function_params: Union[list,dict] = None,
                  model_list: list[model] = None,
                  keep_buildpath: bool = True):
    
#-----------------------------------------------------------------------------#
#-------------------------------VALIDITY CHECK--------------------------------#
#-----------------------------------------------------------------------------#
    
    check = dir_path and target_function and parameters # (anything and None) = None
    if check is None:
        raise Exception("dir_path, target_function and parameters variables cannot be 'None'")
        
    if model_list is None:
        try:
            from ESN_Maker_V4 import ESN_Maker as M
        except Exception as e:
            print(f"Exception raised, see python built-in message: \n\n {e}")
            print("\n\nYou haven't provided an ESN_model of type reservoirpy.model\
                  and ESN_Maker cannot be found.")
            
    if not path.exists(dir_path):
        raise Exception("dir_path is invalid, cannot find where you want to save test data.")
    
    if path.exists(target_function[1]): # imports function from name and path. 
        try:
            spec = importlib.util.spec_from_file_location(name=target_function[0],location=target_function[1])
            loader = importlib.util.LazyLoader(spec.loader)
            spec.loader = loader
            module = importlib.util.module_from_spec(spec)
            sys.modules[target_function[0]] = module
            loader.exec_module(module)
            f_call = getmembers(module,isfunction)[0][1]
            
        except Exception as e:
            print(f"Exception raised, see python built-in message: \n\n {e}")
    
    else:
        raise Exception("target_funcion path or name is invalid.")
    
    try:
        import Useful_Funcs_V4 as UF
        separations = True
    except:
        separations = False
        print("Failed import of Useful_Funcs module, console legibility will be worse.")
    
#-----------------------------------------------------------------------------#
#-------------------DEFINE ESN DEFAULT PARAMETER VALUES-----------------------#
#-----------------------------------------------------------------------------#      
    
    defaults_list = {"node count" : 100,
                     "leak rate" : 0.1,
                     "spectral radius" : 1.0,
                     "connectivity" : 0.1,
                     "input scaling" : 1.0,
                     "input connectivity" : 0.1}
    
#-----------------------------------------------------------------------------#
#-----------------------------GENERATE DATASETS-------------------------------#
#-----------------------------------------------------------------------------#
    
#-------------------------PREPARE SWEEP VARIABLES-----------------------------#

    parameter_names = list(parameters.keys())

    if double_sweep: # if True calculate all unique combinations of the params provided
        combos = list(product(parameter_names,repeat=2))
        for index, combo in enumerate(combos): # check for tuples with set of same values
            if combo[0] == combo[1]:
                combos.pop(index)
           
        for index1, combo1 in enumerate(combos): # check for tuples with same values but inverted order
            for index2,combo2 in enumerate(combos):
                if combo1[0] == combo2[1]:
                    if combo1[1] == combo2[0]:
                        combos.pop(index2)
                        
    else: # if 1D sweep then no combinations needed
        combos = parameter_names

    if separations:
        UF.Sect_Div() # purely for console print aesthetic
    print("LOOP START - GENERATING DATASETS")
    
    for index,combo in enumerate(combos): # for every combination of 2 parameters to sweep
        print(f"working on {combo}")
        
        if index == 0: # at first iteration, the default values are saved separately, for accurate test condition reporting when writing to .JSON
            original_defaults = {}
            for entry in defaults_list:
                original_defaults[entry] = defaults_list[entry]
            original_func_params = {}
            for entry in function_params:
                original_func_params[entry] = function_params[entry]
        
        if double_sweep: # sets sweep start, stop and step
            sweep_param1 = np.arange(parameters[combo[0]][0],
                                     parameters[combo[0]][1] + parameters[combo[0]][2],
                                     parameters[combo[0]][2])
            sweep_param2 = np.arange(parameters[combo[1]][0],
                                     parameters[combo[1]][1] + parameters[combo[1]][2],
                                     parameters[combo[1]][2])
        else:
            sweep_param1 = np.arange(parameters[combo][0],
                                     parameters[combo][1] + parameters[combo][2],
                                     parameters[combo][2])
            sweep_param2 = [0]
        
        for datasets_completed in range(datasets): # for each combination, generate x datasets
            
            seed = randint(0,100) # new seed for each dataset
                
#--------------------------------PERFORM SWEEPS-------------------------------#        
            iteration_no = 0 # counter for ordering .JSON files in SAVE DATA TO .JSON

            for index1,value1 in enumerate( sweep_param1 ):
                for index2,value2 in enumerate( sweep_param2 ): # will only execute once if double_sweep = False
                
                    if type(function_params) == dict: # allows function params to be sweep parameters.
                        count = 0
                        param_found =False
                        for entry in combo: # makes sure current sweep value assigned to correct function_params entry
                            for param in function_params:
                                try:
                                    if param == entry:
                                        param_found = True
                                        if count == 0:
                                            function_params[entry] = value1
                                        else:
                                            function_params[entry] = value2
                                        break
                                except:
                                    pass
                            count +=1
                        if param_found == False:
                            func_params = list(original_func_params.values()) # saves values as list, for passing to f_call
                        else:          
                            func_params = list(function_params.values())
                        
                    else:
                        func_params = function_params # if function params is not a dict, those params cannot be swept, and will only be passed to f_call                
                    if double_sweep:
                        defaults_list[combo[0]] = value1 
                        defaults_list[combo[1]] = value2
                    else:
                        defaults_list[combo] = value1 
                    
                    if model_list is None:
                        AN_ESN = M(nn=1,
                                   out=False,
                                   nc=defaults_list["node count"], 
                                   lr=defaults_list["leak rate"],
                                   sr=defaults_list["spectral radius"],
                                   cny=defaults_list["connectivity"],
                                   ins=defaults_list["input scaling"],
                                   ins_cny=defaults_list["input connectivity"],
                                   init_W='uniform',
                                   rep=True,
                                   seed=seed)
                        
                        model = AN_ESN.networks[0]
                        if training:
                            readout = Ridge(ridge=1e-7) # ridge value suggested as default by reservoirpy.
                            model = model >> readout # ESN comprised of input node, reservoir node of nc neurons, and Ridge output layer
                    
                    else:
                        model = model_list[iteration_no]
                        
                    if gen_input: # generate input if required
                        
                        res_name = model.node_names
                        for name in res_name:
                            if any(x == 'R' for x in name):
                                res_name = name
                                break
                        stream_length = model.get_node(f"{res_name}").get_param("units") * 4                   
                        input_stream = np.random.random([stream_length,1]) - 0.5 # input range [-0.5:0.5]
                        
                        result = f_call(model,
                                        input_stream,
                                        *func_params) #function call with input stream
                                              
                    else:
                        result = f_call(model,
                                        *func_params
                                       ) #function call without input stream                               
                    model = None # to free up memory
                    del AN_ESN # to free up memory
            
#-----------------------------------------------------------------------------#
#-----------------------------SAVE DATA TO .JSON------------------------------#
#-----------------------------------------------------------------------------#

                    """
the code creates a parent folder with the name of the function (f_call) --> test_suite.
it then creates a build folder, where each return value of f_call is saved in its own file.
when the sweep is finished, a test_bed file with the test conditions is created. All the 
files in build are then stitched together and saved in an adjacent directory, called
"function name" + "dataset number". If keep_buildpath is False, build is deleted.
                    """

                    function_name = target_function[0] 
                    test_suite = path.join(dir_path,function_name) # parent folder with function name
                    test_name = target_function[0] + str(datasets_completed + 1) 
                    
                    if not path.exists(test_suite):
                        mkdir(test_suite)
                        
                    test_path = path.join(test_suite,test_name)
                    if not path.exists(test_path):
                        mkdir(test_path)
                        
                    entry_path = path.join(test_path,str(combo))
                    build_path = path.join(test_suite, f"build{combo}")
                    if not path.exists(build_path):
                        mkdir(build_path)
                    
                    """
I kept getting bugs where the files in build were being put together in the wrong order.
This was the quickest fix I could come up with, where instead of numbering each file
with decimal numbers, they are ordered with letters:
    
    data + aaaaaa
    data + aaaaab
    data + aaaaac
    data + aaaaad
    data + aaaaae
    data + aaaaaf
    data + aaaaba
    data + aaaabb
    .
    .
    ..

with 6 letters --> 46656 files can have independent names. if more files are needed,
devise a better solution as this will significantly slow down the program.
                    """
                    
                    suffixes = []
                    for i in range(6):
                        suffixes.append(chr(ord('a') + i))
                    suffix_combos = list((product(suffixes,repeat=len(suffixes))))

                    for i in range(len(suffix_combos)): #convert from array of arrays of strings to array of strings
                       suffix_combos[i] = [word.strip(string.punctuation) for word in str(suffix_combos[i]).split() if word.strip(string.punctuation).isalnum()]
                       dummy = ''
                       for letter in suffix_combos[i]:
                           dummy = dummy + letter
                       suffix_combos[i]= dummy
                    data_loc = path.join(build_path,f"data_{suffix_combos[iteration_no]}")
                    
                    with open(data_loc, "w") as outfile: # create file and save result
                        json.dump(result, outfile)
                        outfile.close()
                    
                    iteration_no +=1
                    
            del suffix_combos # free up memory
            test_bed = {} # create dict for storing test bed conditions
            test_bed.update(original_defaults) # add default ESN parameters
            test_bed.update(original_func_params) # add default function parameters
            
            for entry in combo:
                test_bed[entry] = parameters[entry] # replace default ESN parameters with sweep parameter bounds          
            for entry in test_bed:
                if (type(test_bed[entry])) == np.int32: # JSON dislikes np.int32 and throws serialization error     
                    test_bed[entry] = int(test_bed[entry])
            
            test_bed_loc = path.join(build_path,"test bed") # create test bed file in build  
            with open(test_bed_loc, "w") as outfile:
                json.dump(test_bed, outfile)
                outfile.close()
            
            files = list()
            for filename in listdir(build_path): 
                    
                if filename != "test bed": # more legible if inserted at top of file
                    files.append(path.join(build_path,filename)) # list of all files to stitch together
                    
            files.insert(0, test_bed_loc) # add test bed to top
            
            newfile = list()            
            for f2 in files: # stitch all the files together
                with open(f2, 'r') as infile:
                    newfile.append(json.load(infile))
                    infile.close()
    
                with open(entry_path, 'w') as output_file:
                    json.dump(newfile, output_file,sort_keys=False, indent=0,separators=(',',':'))
                    output_file.close()
            
            if not keep_buildpath: 
                shutil.rmtree(build_path) # delete build
            
                    











