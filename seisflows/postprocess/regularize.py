
import sys
import numpy as np

from seisflows.tools import unix
from seisflows.tools.array import loadnpy, savenpy
from seisflows.tools.array import grid2mesh, mesh2grid, stack
from seisflows.tools.tools import exists
from seisflows.config import  ParameterError, custom_import
from seisflows.tools.math import nabla


PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

system = sys.modules['seisflows_system']
solver = sys.modules['seisflows_solver']
preprocess = sys.modules['seisflows_preprocess']


class regularize(custom_import('postprocess', 'base')):
    """ Adds penalty function regularization options to base class

        This parent class is only an abstract base class; see child classes
        TIKHONOV1, TIKHONOV1, and TOTAL_VARIATION for usable regularization.

        Prior to regularizing gradient, near field artifacts must be corrected.
        The "FIXRADIUS" parameter specifies the radius, in number of GLL points,
        within which the correction is applied.
    """

    def check(self):
        """ Checks parameters and paths
        """
        super(regularize, self).check()

        if 'FIXRADIUS' not in PAR:
            setattr(PAR, 'FIXRADIUS', 7.5)

        if 'LAMBDA' not in PAR:
            setattr(PAR, 'LAMBDA', 0.)


    def write_gradient(self, path):
        #super(regularize, self).write_gradient(path)

        if not exists(path):
            raise Exception

        #system.run_single('postprocess', 'process_kernels',
	self.process_kernels(
                 path=path+'/kernels',
                 parameters=solver.parameters)

        g = solver.load(path +'/'+ 'kernels/sum', parameters=solver.parameters, suffix='_kernel')
        #if not PAR.LAMBDA:
        #    return solver.merge(g)

        m = solver.load(path +'/'+ 'model')
        mesh = self.getmesh()

        for key in solver.parameters:
            for iproc in range(PAR.NPROC):
                g[key][iproc] += PAR.LAMBDA *\
                    self.nabla(mesh, m[key][iproc], g[key][iproc])

        self.save(solver.merge(g), path)


    def process_kernels(self, path, parameters):
        """ Processes kernels in accordance with parameter settings
        """
        assert exists(path)

        system.run_single('solver', 'combine',
	#solver.combine(
                   input_path=path,
                   output_path=path+'/'+'sum',
                   parameters=parameters)

        if exists(path +'/'+ 'sum'):
            unix.mv(path +'/'+ 'sum', path +'/'+ 'sum_nofix')

        # mask sources and receivers
	self.fix_near_field(path=path)



    def fix_near_field(self, path=''):
        """
        """
        #import preprocess
	preprocess = sys.modules['seisflows_preprocess']
        preprocess.setup()

        #name = solver.source_names[solver.taskid]
	name = 'sum_nofix'
        fullpath = path +'/'+ name
        g = solver.load(fullpath, suffix='_kernel')
        if not PAR.FIXRADIUS:
            return

        x,z = self.getxz()

        lx = x.max() - x.min()
        lz = z.max() - z.min()
        nn = x.size
        nx = np.around(np.sqrt(1.0*nn*lx/lz))
        nz = np.around(np.sqrt(1.0*nn*lz/lx))
        dx = 1.0*lx/nx
        dz = 1.0*lz/nz

        sigma = 0.5*PAR.FIXRADIUS*(dx+dz)

	sx = []
	sy = []
	sz = []
	for source_name in solver.source_names:
            ssx, ssy, ssz = preprocess.get_source_coords(
                preprocess.reader(
            	    PATH.SOLVER+'/'+source_name+'/'+'traces/obs', solver.data_filenames[0]))
	    sx.append(ssx[0])
	    sy.append(ssy[0])
	    sz.append(ssz[0])

        # mask sources
	for isrc in range(PAR.NSRC):
            mask = np.exp(-0.5*((x-sx[isrc])**2.+(z-sy[isrc])**2.)/sigma**2.)
            for key in solver.parameters:
            	weight = np.sum(mask*g[key][0])/np.sum(mask)
            	g[key][0] *= 1.-mask
            	g[key][0] += mask*weight

        rx, ry, rz = preprocess.get_receiver_coords(
            preprocess.reader(
                solver.cwd+'/'+'traces/obs', solver.data_filenames[0]))

        # mask receivers
        for ir in range(PAR.NREC):
            mask = np.exp(-1.5*((x-rx[ir])**2.+(z-ry[ir])**2.)/sigma**2.)
            for key in solver.parameters:
                weight = np.sum(mask*g[key][0])/np.sum(mask)
                g[key][0] *= 1.-mask
                g[key][0] += mask*weight

        solver.save(g, path+'/'+ 'sum', parameters=solver.parameters, suffix='_kernel')


    def nabla(self, mesh, m, g):
        raise NotImplementedError("Must be implemented by subclass.")


    def getmesh(self):
        model_path = PATH.OUTPUT +'/'+ 'model_init'
        solver = sys.modules['seisflows_solver']
        try:
            m = solver.load(model_path)
            x = m['x'][0]
            z = m['z'][0]
            mesh = stack(x.flatten(), z.flatten())
        except:
            x = solver.io.read_slice(model_path, 'x', 0)
            z = solver.io.read_slice(model_path, 'z', 0)
            mesh = stack(x[0], z[0])
        return mesh


    def getxz(self):
        model_path = PATH.OUTPUT +'/'+ 'model_init'
        solver = sys.modules['seisflows_solver']
        try:
            m = solver.load(model_path)
            x = m['x'][0]
            z = m['z'][0]
        except:
            x = solver.io.read_slice(model_path, 'x', 0)
            z = solver.io.read_slice(model_path, 'z', 0)
        #return x, z
        return np.array(x).flatten(), np.array(z).flatten()


