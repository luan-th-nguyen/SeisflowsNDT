
import os
import sys

from os.path import abspath, basename, join, dirname
from seisflows.tools import unix
from seisflows.tools.tools import call, findpath, saveobj
from seisflows.config import ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class pbs_torque_sm(custom_import('system', 'base')):
    """ An interface through which to submit workflows, run tasks in serial or
      parallel, and perform other system functions.

      By hiding environment details behind a python interface layer, these
      classes provide a consistent command set across different computing
      environments.

      Intermediate files are written to a global scratch path PATH.SCRATCH,
      which must be accessible to all compute nodes.

      Optionally, users can provide a local scratch path PATH.LOCAL if each
      compute node has its own local filesystem.

      For important additional information, please see
      http://seisflows.readthedocs.org/en/latest/manual/manual.html#system-configuration
    """

    def check(self):
        """ Checks parameters and paths
        """

        # check parameters
        if 'TITLE' not in PAR:
            setattr(PAR, 'TITLE', basename(abspath('.')))

        # time allocated for workflow in minutes
        if 'WALLTIME' not in PAR:
            setattr(PAR, 'WALLTIME', 30.)

        if 'MEMORY' not in PAR:
            raise ParameterError(PAR, 'MEMORY')

        if 'VERBOSE' not in PAR:
            setattr(PAR, 'VERBOSE', 1)

        # number of tasks
        if 'NTASK' not in PAR:
            raise ParameterError(PAR, 'NTASK')

        # number of cores per task
        if 'NPROC' not in PAR:
            raise ParameterError(PAR, 'NPROC')

        # number of requested nodes
        if 'NODES' not in PAR:
            raise ParameterError(PAR, 'NODES')

        # number of cores per node
        if 'NODESIZE' not in PAR:
            raise ParameterError(PAR, 'NODESIZE')

        # optional additional PBS arguments
        if 'PBSARGS' not in PAR:
            setattr(PAR, 'PBSARGS', '')

        # how to invoke executables
        if 'MPIEXEC' not in PAR:
            setattr(PAR, 'MPIEXEC', '')

        # optional environment variable list VAR1=val1,VAR2=val2,...
        if 'ENVIRONS' not in PAR:
            setattr(PAR, 'ENVIRONS', '')

        # level of detail in output messages
        if 'VERBOSE' not in PAR:
            setattr(PAR, 'VERBOSE', 1)

        # where job was submitted
        if 'WORKDIR' not in PATH:
            setattr(PATH, 'WORKDIR', abspath('.'))

        # check paths
        if 'SCRATCH' not in PATH:
            setattr(PATH, 'SCRATCH', join(abspath('.'), 'scratch'))

        if 'LOCAL' not in PATH:
            setattr(PATH, 'LOCAL', None)

        if 'SYSTEM' not in PATH:
            setattr(PATH, 'SYSTEM', join(PATH.SCRATCH, 'system'))

        if 'SUBMIT' not in PATH:
            setattr(PATH, 'SUBMIT', abspath('.'))

        if 'OUTPUT' not in PATH:
            setattr(PATH, 'OUTPUT', join(PATH.SUBMIT, 'output'))


    def submit(self, workflow):
        """Submits job
        """
        # create scratch directories
        unix.mkdir(PATH.SCRATCH)
        unix.mkdir(PATH.SYSTEM)

        # create output directories
        unix.mkdir(PATH.OUTPUT)
        #unix.cd(PATH.OUTPUT)

        # save current state
        self.checkpoint()

        # construct resource list
        #nodes = int(PAR.NTASK / PAR.NODESIZE)
	nodes = PAR.NODES
        cores = PAR.NTASK % PAR.NODESIZE
        hours = int(PAR.WALLTIME / 60)
        minutes = PAR.WALLTIME % 60
        resources = 'walltime=%02d:%02d:00'%(hours, minutes)
        #if nodes == 0:
        #    resources += ',mem=%dgb,nodes=1:ppn=%d'%(PAR.MEMORY, cores)
        #elif cores == 0:
        #    resources += ',mem=%dgb,nodes=%d:ppn=%d'%(PAR.MEMORY, nodes, PAR.NODESIZE)
        #else:
        #    resources += ',mem=%dgb,nodes=%d:ppn=%d+1:ppn=%d'%(PAR.MEMORY, nodes, PAR.NODESIZE, cores)
        resources += ',nodes=%d:ppn=%d'%(nodes, PAR.NODESIZE)

        # construct arguments list
        #call('qsub '
        #        + '%s ' % PAR.PBSARGS
        #        + '-N %s ' % PAR.TITLE
        #        + '-o %s ' %( PATH.SUBMIT +'/'+ 'output.log')
        #        + '-l %s ' % resources
        #        + '-q %s ' % 'medium'
        #        + '-j %s ' % 'oe'
        #        + findpath('seisflows.system') +'/'+ 'wrappers/submit '
        #        + '-F %s ' % PATH.OUTPUT)
        cmd =   'qsub ' \
                + '%s ' % PAR.PBSARGS \
                + '-N %s ' % PAR.TITLE \
                + '-o %s ' %( PATH.WORKDIR +'/'+ 'output.log') \
                + '-l %s ' % resources \
                + '-j %s ' % 'oe' \
                + '-F "%s" ' % PATH.OUTPUT \
                + findpath('seisflows.system') + '/'+'wrappers/submit ' \
                + '-F %s' % PATH.OUTPUT

	print cmd
	call(cmd)

    def run(self, classname, funcname, hosts='all', **kwargs):
        """  Runs tasks in serial or parallel on specified hosts
        """
        self.checkpoint()
        self.save_kwargs(classname, funcname, kwargs)
	PYTHONPATH = '/data/GZB/luan/seisflows_ndt/:/home/luan/miniconda2/lib/python27.zip:/home/luan/miniconda2/lib/python2.7:/home/luan/miniconda2/lib/python2.7/plat-linux2:/home/luan/miniconda2/lib/python2.7/lib-tk:/home/luan/miniconda2/lib/python2.7/lib-old:/home/luan/miniconda2/lib/python2.7/lib-dynload:/home/luan/miniconda2/lib/python2.7/site-packages:/home/luan/miniconda2/lib/python2.7/site-packages/cycler-0.10.0-py2.7.egg:/home/luan/miniconda2/lib/python2.7/site-packages/setuptools-27.2.0-py2.7.egg'

        if hosts == 'all':
            # run on all available nodes
            #cmd =   'pbsdsh ' \
            #        + join(findpath('seisflows.system'), 'wrappers/export_paths.sh ') \
            #        + os.getenv('PATH') + ' ' \
            #        + os.getenv('LD_LIBRARY_PATH') + ' ' \
            #        + join(findpath('seisflows.system'), 'wrappers/run_pbsdsh ') \
            #        + PATH.OUTPUT + ' ' \
            #        + classname + ' ' \
            #        + funcname + ' ' \
            #        + 'PYTHONPATH='+findpath('seisflows')+',' \
	    #	    + PAR.ENVIRONS

            cmd =   'pbsdsh ' \
                    + findpath('seisflows.system') +'wrappers/run_torque_pbsdsh ' \
                    + PATH.OUTPUT + ' ' \
                    + classname + ' ' \
                    + funcname + ' ' \
                    + 'SEISFOWSPATH='+findpath('seisflows.system') + ',' \
                    + 'PATH='+os.getenv('PATH') + ',' \
                    + 'PYTHONPATH='+PYTHONPATH 

            #cmd =   'pbsdsh ' \
            #        + findpath('seisflows.system') +'wrappers/test ' \
            #        + PATH.OUTPUT + ' ' \
            #        + classname + ' ' \
            #        + funcname + ' ' \
            #        + 'SEISFOWSPATH='+findpath('seisflows.system') + ',' \
            #        + 'PYTHONPATH='+os.getenv('PATH') 

	    print cmd

	    call(cmd)

        elif hosts == 'head':
            # run on head node
            #call('pbsdsh '
            #        + join(findpath('seisflows.system'), 'wrappers/export_paths.sh ')
            #        + os.getenv('PATH') + ' '
            #        + os.getenv('LD_LIBRARY_PATH') + ' '
            #        + join(findpath('seisflows.system'), 'wrappers/run_pbsdsh_head ')
            #        + PATH.OUTPUT + ' '
            #        + classname + ' '
            #        + funcname + ' '
            #        + 'PYTHONPATH='+findpath('seisflows')+',' 
	    #	     + PAR.ENVIRONS)

            cmd =   'pbsdsh ' \
                    + findpath('seisflows.system') +'wrappers/run_torque_pbsdsh ' \
                    + PATH.OUTPUT + ' ' \
                    + classname + ' ' \
                    + funcname + ' ' \
                    + 'SEISFOWSPATH='+findpath('seisflows.system') + ',' \
                    + 'PATH='+os.getenv('PATH') + ',' \
                    + 'PYTHONPATH='+PYTHONPATH

            #cmd =   'pbsdsh ' \
            #        + findpath('seisflows.system') +'wrappers/test ' \
            #        + PATH.OUTPUT + ' ' \
            #        + classname + ' ' \
            #        + funcname + ' ' \
            #        + 'SEISFOWSPATH='+findpath('seisflows.system') + ',' \
            #        + 'PYTHONPATH='+os.getenv('PATH') 

	    print cmd

    def getnode(self):
        """ Gets number of running task
        """
        return int(os.getenv('PBS_VNODENUM'))


    def mpiexec(self):
        """ Specifies MPI exectuable; used to invoke solver
        """
        # call solver as MPI singleton when using pbsdsh
        #return ''
        return PAR.MPIEXEC


    #def save_kwargs(self, classname, funcname, kwargs):
    #    kwargspath = join(PATH.OUTPUT, 'SeisflowsObjects', classname+'_kwargs')
    #    kwargsfile = join(kwargspath, funcname+'.p')
    #    unix.mkdir(kwargspath)
    #    saveobj(kwargsfile, kwargs)
    def save_kwargs(self, classname, method, kwargs):
        kwargspath = join(PATH.OUTPUT, 'kwargs')
        kwargsfile = join(kwargspath, classname+'_'+method+'.p')
        unix.mkdir(kwargspath)
        saveobj(kwargsfile, kwargs)

