
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


    def compute_direction(self):
        super(ADAM, self).compute_direction()


    def restart(self):
        # steepest descent never requires restarts
        pass

