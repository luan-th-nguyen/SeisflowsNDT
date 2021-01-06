
import sys
import numpy as np

from seisflows.config import custom_import, ParameterError

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class ADAM(custom_import('optimize', 'base')):
    """ mini-batch ADAM (Adaptive moment estimation) method
    """
    restarted = False

    def check(self):
        """ Checks parameters, paths, and dependencies
        """

        if 'LINESEARCH' not in PAR:
            setattr(PAR, 'LINESEARCH', 'Bracket')

        super(ADAM, self).check()


    def setup(self):
        super(ADAM, self).setup()
        self._beta1 = 0.9
        self._beta2 = 0.999
        self._eps = 1.0e-8
        self._v = 0
        self._s = 0


    def compute_direction(self):
        """ Computes search direction
        """
        g_new = self.load('g_new')

        self._v = self._beta1*self._v + (1. - self._beta1)*g_new
        self._s = self._beta2*self._s + (1. - self._beta2)*g_new**2

        v_corrected = self._v/(1. - self._beta1**self.iter)
        s_corrected = self._s/(1. - self._beta2**self.iter)

        g_new = v_corrected/(s_corrected**0.5 + self._eps)

        if self.precond:
            p_new = -self.precond(g_new)
        else:
            p_new = -g_new
        self.save('p_new', p_new)


    def restart(self):
        # steepest descent never requires restarts
        pass

