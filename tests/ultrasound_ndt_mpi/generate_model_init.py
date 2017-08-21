#!/usr/bin/env python

import sys
sys.path.insert(0,'../../seisflows/plugins/solver_io')
#print sys.path
from fortran_binary import read_slice, write_slice


if __name__ == "__main__":
    """ Generate homogeneous initial model
	using data from /model_true
	USAGE
	    ./generate_model_init.py
    """

    input_path = './model_true'
    output_path = './model_init'

    parameters = ['rho','vp','vs'] 
    nproc = 4

    RHO = 2300.0
    VP = 3600.0 
    VS = 1900.0
    consts = {'rho':RHO,'vp':VP,'vs':VS} 
    modelslice = {}

    # write data
    for par in parameters:
        modelslice[par] = []
        for iproc in range(nproc):
            modelslice[par] = read_slice(input_path, par, iproc)
	    modelslice[par][0].fill(consts[par])
            write_slice(modelslice[par][0], output_path, par, iproc)

    # write coordinates
    for par in ['x','z']:
	for iproc in range(nproc):
            modelslice[par] = read_slice(input_path, par, iproc)
            write_slice(modelslice[par][0], output_path, par, iproc)
