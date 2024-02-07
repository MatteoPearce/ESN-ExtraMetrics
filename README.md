# ESN-ExtraMetrics
Extra Metrics for the characterisation of Echo State Networks in the context of Reservoir Computing.

Over the summer of 2023 I worked for the University of York's Computer Science Department, tasked with exploring extra metrics beyond the standard measures of Kernel Rank, Generalisation Rank, and Linear Memory Capacity, typically used to characterise the behaviour space of substrates for Reservoir Computing, a novel machine learning technique. I have created this repository to showcase my work and Python programming proficiency.

Echo State Networks were the proverbial Guinea Pig for my work, as they are the benchmark behaviour-space substrate in accordance with the CHARC framework. This is a project that endeavours to create a benchmarking environment for the description of the N-dimensional feature space of substrates for reservoir computing. The end goal is to create an encyclopedia of behaviour spaces for substrates such that researchers can gain insight into which might be advantageous for their use case. This framework is set out in the following paper:
https://arxiv.org/abs/1810.07135

I used the ReservoirPy & NumPy libraries extensively, achieving comfortable fluency in both. At the end of my employment, I had provided an implementation of Shannon Entropy with history, and of Nth order Memory Capacity algorithms, as well as a toolkit for generating useful datasets and displaying the results graphically, both as single parameter sweeps, or as heatmaps for the purposes of assessing correlations between parameters and desired metric calculations.

Please see the documentation provided, as well as the header comments within the scripts themselves, to better understand the toolkit framework and the implementation of algorithms. I created this framwork with modularity in mind, such that any future metric algorithms can seamlessy interface with the data generation scripts and the display scripts, provided the programmer adheres to a set of design rules. 
