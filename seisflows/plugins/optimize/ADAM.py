import numpy as np

from seisflows.tools import unix
from seisflows.tools.tools import savetxt, exists, loadnpy, savenpy


class ADAM(object):
    """ Adaptive moment estimation
    """
    def __init__(self, path='.', load=loadnpy, save=savenpy, precond=None):
        assert exists(path)
        unix.cd(path)
        #unix.mkdir('ADAM')

        self.path = path
        self.load = load
        self.save = save
        self.precond = precond
        self._beta1 = 0.9
        self._beta2 = 0.999
        self._eps = 1.0e-8

        self.iter = 0
        self.initialize()

    
    def initialize(self):
        unix.mkdir(self.path+'/'+'ADAM')
        unix.cd(self.path)

        self.iter += 1
        v = 0.
        s = 0.
        self.save('ADAM/v', v)
        self.save('ADAM/s', s)


    def __call__(self):
        """ Returns ADAM search direction
        """
        self.iter += 1

        unix.cd(self.path)
        g = self.load('g_new')
        v = self.load('ADAM/v')
        s = self.load('ADAM/s')

        v = self._beta1*v + (1. - self._beta1)*g
        s = self._beta2*s + (1. - self._beta2)*g**2

        v_corrected = v/(1. - self._beta1**self.iter)
        s_corrected = s/(1. - self._beta2**self.iter)

        g = v_corrected/(s_corrected**0.5 + self._eps)

        self.save('ADAM/v', v)
        self.save('ADAM/s', s)

        if self.precond:
            return -self.precond(g)
        else:
            return -g

