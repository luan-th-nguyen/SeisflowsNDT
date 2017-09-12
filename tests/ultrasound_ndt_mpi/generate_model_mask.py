#!/usr/bin/env python

import sys
sys.path.insert(0,'../../seisflows/plugins/solver_io')
from fortran_binary import read_slice, write_slice
sys.path.insert(0,'../../seisflows/tools')
from seisflows.tools.array import meshsmooth, append, stack
import os
from os.path import isdir, exists, getsize
import numpy as np



def read_multislice(model_in, NSLICE, parameter):
    """ Reads NSLICE slices of the model using read_fortran(filename)
    """
    # initialize data and coordinates
    v = []
    coords = {}
    for key in ['x', 'z']:
 	coords[key] = []

    # read data and coordinates
    for iproc in range(NSLICE):
	v += read_slice(model_in,parameter,iproc)
    for key in ['x', 'z']:
	for iproc in range(NSLICE):
	    coords[key] += read_slice(model_in,key,iproc)

    return coords, v


if __name__ == '__main__':
    """ Generate 2D mask

      USAGE
          ./generate_model_mask.py  model_true  model_mask 4  vs
    """
    # parse command line arguments
    model_in = sys.argv[1]
    mask_out = sys.argv[2]
    NSLICE = int(sys.argv[3])
    parameter = sys.argv[4]


    # read all model slices and process
    parameters = ['vs','vp']
    for key in parameters:
    	coords, v = read_multislice(model_in,NSLICE,key)
	for iproc in range(NSLICE):
	    v[iproc].fill(1.0)
            z_idx = np.where(coords['z'][iproc] > 175)
	    v[iproc][z_idx] = 0.0

	mesh = stack(coords['x'][0], coords['z'][0])
	for iproc in range(NSLICE-1):
            mesh = append(mesh,stack(coords['x'][iproc+1], coords['z'][iproc+1]))
        v[:] = meshsmooth(v[:], mesh, 4.0)

        # write out slices
	for iproc in range(NSLICE):
            write_slice(v[iproc], mask_out, key , iproc)

	# write out coordinates
	for key in ['x','z']:
	    for iproc in range(NSLICE):
            	write_slice(coords[key][iproc], mask_out, key , iproc)
