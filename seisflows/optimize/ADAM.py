
import sys
import numpy as np

from seisflows.config import custom_import, ParameterError
from seisflows.plugins import optimize

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

        self.ADAM = getattr(optimize, 'ADAM')(
            path=PATH.OPTIMIZE,
            precond=self.precond)


    def compute_direction(self):
        """ Computes search direction
        """
        p_new = self.ADAM()
        self.save('p_new', p_new)


    def restart(self):
        # steepest descent never requires restarts
        pass

