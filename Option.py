# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 13:26:23 2022

@author: joshchien
"""

#%%
from QuantLib import *
import numpy as Numpy
import matplotlib.pyplot as Matplotlib

# method for simulating paths for the both uncorrelated and correlated processes
# arguments:
# process = QuantLib 1-dimensional stochastic process object or 
#           StochasticProcessArray (Array of correlated 1-D stochastic processes)
# timeGrid = QuantLib TimeGrid object
# n = number of paths
def GeneratePaths(process, timeGrid, n):

# correlated processes, use GaussianMultiPathGenerator
    if(type(process) == StochasticProcessArray):
        times = []; [times.append(timeGrid[t]) for t in range(len(timeGrid))]        
        nGridSteps = (len(times) - 1) * process.size()
        sequenceGenerator = UniformRandomSequenceGenerator(nGridSteps, UniformRandomGenerator())
        gaussianSequenceGenerator = GaussianRandomSequenceGenerator(sequenceGenerator)
        pathGenerator = GaussianMultiPathGenerator(process, times, gaussianSequenceGenerator, False)        
        paths = Numpy.zeros(shape = (n, process.size(), len(timeGrid)))

# loop through number of paths
        for i in range(n):
# request multiPath, which contains the list of paths for each process
            multiPath = pathGenerator.next().value()
# loop through number of processes
        for j in range(multiPath.assetNumber()):
# request path, which contains the list of simulated prices for a process
            path = multiPath[j]
# push prices to array
            paths[i, j, :] = Numpy.array([path[k] for k in range(len(path))])
# resulting array dimension: n, process.size(), len(timeGrid)
            return paths

# uncorrelated processes, use GaussianPathGenerator
    else:
        sequenceGenerator = UniformRandomSequenceGenerator(len(timeGrid), UniformRandomGenerator())
        gaussianSequenceGenerator = GaussianRandomSequenceGenerator(sequenceGenerator)
        maturity = timeGrid[len(timeGrid) - 1]
        pathGenerator = GaussianPathGenerator(process, maturity, len(timeGrid), gaussianSequenceGenerator, False)
        paths = Numpy.zeros(shape = (n, len(timeGrid)))   
        for i in range(n):
            path = pathGenerator.next().value()
            paths[i, :] = Numpy.array([path[j] for j in range(len(timeGrid))])
# resulting array dimension: n, len(timeGrid)
            return paths

#%%
# create simulation-related parameters
today = Date(30, November, 2018)
maturity = 5.0
nSteps = int(maturity) * 365
# create regularly spaced QuantLib TimeGrid object
timeGrid = TimeGrid(maturity, nSteps)
nPaths = 25

# create HW1F model
reversionSpeed = 0.05
rateVolatility = 0.0099255
curve = RelinkableYieldTermStructureHandle(FlatForward(today, 0.01, Actual360()))
HW1F = HullWhiteProcess(curve, reversionSpeed, rateVolatility)
hw1f_paths = GeneratePaths(HW1F, timeGrid, nPaths)

# create GBM model
initialValue = 0.01
mue = 0.01
sigma = 0.0099255
GBM = GeometricBrownianMotionProcess(initialValue, mue, sigma)
gbm_paths = GeneratePaths(GBM, timeGrid, nPaths)

# plot uncorrelated paths
times = []; [times.append(timeGrid[t]) for t in range(len(timeGrid))]
Matplotlib.rcParams['figure.figsize'] = [12.0, 8.0]
f, subPlots = Matplotlib.subplots(2, sharex = True)
f.suptitle('Uncorrelated paths n=' + str(nPaths))
subPlots[0].set_title('HW1F')
subPlots[1].set_title('GBM')

for i in range(hw1f_paths.shape[0]):
    path = hw1f_paths[i, :] 
    subPlots[0].plot(times, path)

for i in range(gbm_paths.shape[0]):
    path = gbm_paths[i, :] 
    subPlots[1].plot(times, path)

# create correlated paths
rho = 1.0
correlation = [[1.0, rho], [rho, 1.0]]
processArray = StochasticProcessArray([HW1F, GBM], correlation)
correlated_paths = GeneratePaths(processArray, timeGrid, nPaths)

# plot correlated paths
f2, subPlots2 = Matplotlib.subplots(processArray.size(), sharex = True)
f2.suptitle('Correlated paths n=' + str(nPaths) + ', rho=' + str(rho))
subPlots2[0].set_title('HW1F')
subPlots2[1].set_title('GBM')

for i in range(nPaths):
    for j in range(processArray.size()):
        path = correlated_paths[i, j, :]
        subPlots2[j].plot(times, path)