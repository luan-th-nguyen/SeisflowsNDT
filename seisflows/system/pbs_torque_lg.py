
import os
import math
import sys
import time

from os.path import abspath, basename, join
from seisflows.tools import msg
from seisflows.tools import unix
from seisflows.tools.tools import call, findpath, saveobj
from seisflows.config import ParameterError, custom_import

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']

# Workarounds for TORQUE 4.2.9
# Run PAR.NTASK in a job-array, each mpi job is run on PAR.NPROC processes
class pbs_torque_lg(custom_import('system', 'base')):
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
        # name of job
        if 'TITLE' not in PAR:
            setattr(PAR, 'TITLE', basename(abspath('.')))

        # time allocated for workflow in minutes
        if 'WALLTIME' not in PAR:
            setattr(PAR, 'WALLTIME', 30.)

        # number of tasks
        if 'NTASK' not in PAR:
            raise ParameterError(PAR, 'NTASK')

        # size of mini-batches
        if 'NMINIBATCH' not in PAR:
            setattr(PAR, 'NMINIBATCH', PAR.NTASK)

        # number of cores per task
        if 'NPROC' not in PAR:
            raise ParameterError(PAR, 'NPROC')

        # number of requested nodes
        #if 'NODES' not in PAR:
        #    raise ParameterError(PAR, 'NODES')

        # number of cores per node
        if 'NODESIZE' not in PAR:
            raise ParameterError(PAR, 'NODESIZE')

        # how to invoke executables
        if 'MPIEXEC' not in PAR:
            setattr(PAR, 'MPIEXEC', 'mpirun')

        # optional additional PBS arguments
        if 'PBSARGS' not in PAR:
            setattr(PAR, 'PBSARGS', '')

        # optional environment variable list VAR1=val1,VAR2=val2,...
        if 'ENVIRONS' not in PAR:
            setattr(PAR, 'ENVIRONS', '')

        # level of detail in output messages
        if 'VERBOSE' not in PAR:
            setattr(PAR, 'VERBOSE', 1)

        # where job was submitted
        if 'WORKDIR' not in PATH:
            setattr(PATH, 'WORKDIR', abspath('.'))

        # where output files are written
        if 'OUTPUT' not in PATH:
            setattr(PATH, 'OUTPUT', PATH.WORKDIR+'/'+'output')

        # where temporary files are written
        if 'SCRATCH' not in PATH:
            setattr(PATH, 'SCRATCH', PATH.WORKDIR+'/'+'scratch')

        # where system files are written
        if 'SYSTEM' not in PATH:
            setattr(PATH, 'SYSTEM', PATH.SCRATCH+'/'+'system')

        # optional local scratch path
        if 'LOCAL' not in PATH:
            setattr(PATH, 'LOCAL', None)


    def submit(self, workflow):
        """ Submits workflow
        """
        # create scratch directories
        unix.mkdir(PATH.SCRATCH)
        unix.mkdir(PATH.SYSTEM)

        # create output directories
        unix.mkdir(PATH.OUTPUT)
        unix.mkdir(PATH.WORKDIR+'/'+'output.pbs')

        workflow.checkpoint()

        hours = PAR.WALLTIME/60
        minutes = PAR.WALLTIME%60
        resources = 'walltime=%02d:%02d:00' % (hours, minutes)

        #nodes = PAR.NODES 
	#ncpus = PAR.NODESIZE
	nodes = 1
	ncpus = 1

        resources += ',nodes=%d:ppn=%d'%(nodes, ncpus)

        # prepare qsub arguments
        cmd =   'qsub ' \
                + '-N %s ' % PAR.TITLE \
                + '-l %s ' % resources \
                + '-o %s ' %( PATH.WORKDIR +'/'+ 'output.log') \
                + '-j %s ' % 'oe' \
		+ '-V ' \
                + findpath('seisflows.system') + '/'+'wrappers/submit ' \
                + '-F %s' % PATH.OUTPUT

	# run command on head node
        #cmd =   findpath('seisflows.system') + '/'+'wrappers/submit ' \
        #        + PATH.OUTPUT

	#print cmd
	call(cmd)


    def run(self, classname, method, hosts='all', **kwargs):
        """ Executes the following task:
              classname.method(*args, **kwargs)
        """
        self.checkpoint(PATH.OUTPUT, classname, method, hosts, kwargs)

        jobs = self.submit_job_array(classname, method, hosts)
        while True:
            # wait a few seconds before checking again
            time.sleep(5)
            self._timestamp()
            isdone, jobs = self.job_array_status(classname, method, jobs)
            if isdone:
		#print 'Job-array is finished' # testing
                return


    def run_single(self, classname, method, hosts='head', **kwargs):
        """ Executes task a single  time
              classname.method(*args, **kwargs)
        """
        self.checkpoint(PATH.OUTPUT, classname, method, hosts, kwargs)

        jobs = self.submit_job_array(classname, method, hosts)
        while True:
            # wait a few seconds before checking again
            time.sleep(5)
            self._timestamp()
            isdone, jobs = self.job_array_status(classname, method, jobs)
            #print isdone, jobs
            if isdone:
		# wait a few more seconds
                time.sleep(5)
                return


    def mpiexec(self):
        """ Specifies MPI executable used to invoke solver
        """
        return PAR.MPIEXEC


    def taskid(self):
        """ Provides a unique identifier for each running task
        """
        try:
            #return os.getenv('PBS_ARRAY_INDEX')
            return int(os.getenv('PBS_ARRAYID'))
        except:
            #raise Exception("PBS_ARRAY_INDEX environment variable not defined.")
            raise Exception("PBS_ARRAYID environment variable not defined.")


    ### private methods

    def submit_job_array(self, classname, method, hosts='all'):
        with open(PATH.SYSTEM+'/'+'job_id', 'w') as f:
            call(self.job_array_cmd(classname, method, hosts),
                stdout=f)

        # retrieve job id (only one job_id of the job-array is run at a time)
        with open(PATH.SYSTEM+'/'+'job_id', 'r') as f:
            line = f.readline()
            job = line.split()[-1].strip()
	#print 'job-array is: %s' % job  # testing
	#print 'hosts is: %s' % hosts	  # testing
	return [job]		  # testing


    def job_array_cmd(self, classname, method, hosts):
        nodes = math.ceil(PAR.NTASK*PAR.NPROC/float(PAR.NODESIZE))
        ncpus = PAR.NPROC
        mpiprocs = PAR.NPROC

        hours = PAR.TASKTIME/60
        minutes = PAR.TASKTIME%60
        resources = 'walltime=%02d:%02d:00'%(hours, minutes)

        #resources += ',nodes=%d:ppn=%d:procs=%d'%(nodes,ncpus,mpiprocs)
        #resources += ',nodes=%d:ppn=%d'%(nodes,ncpus)

        resources += ',nodes=%d:ppn=%d'%(1,4)	# medium
        #resources += ',nodes=%d:ppn=%d'%(2,4)	# large

	# ssh is needed because qsub from compute nodes are not allowed
        cmd =   'ssh luan@master ' \
		+ 'qsub ' \
                + '%s ' % PAR.PBSARGS \
		+ '-l %s ' % resources \
                + '-N %s ' % PAR.TITLE \
                + '-o %s ' % (PATH.WORKDIR+'/'+'output.pbs/'+ '${PBS_ARRAYID}') \
                + '-j %s ' % 'oe' \
		+ '-V ' \
                + self.job_array_args(hosts)  \
                + '-F %s' % PATH.OUTPUT + ',' \
                + classname + ',' \
                + method + ',' \
                + 'SEISFLOWSPATH='+findpath('seisflows.system')

	#print cmd
	return cmd

    def job_array_args(self, hosts):
        if hosts == 'all':
          #args = ('-J 0-%s ' % (PAR.NTASK-1)
          #      +'-o %s ' % (PATH.WORKDIR+'/'+'output.pbs/' + '${PBS_ARRAYID}')
          #      + ' -- ' + findpath('seisflows.system') +'/'+ 'wrappers/run ')
          args = ('-t 0-%s ' % (PAR.NTASK-1)
                + findpath('seisflows.system') +'/'+ 'wrappers/run_torque ')

        elif hosts == 'head':
          #args = ('-J 0-0 '
          #       +'-o %s ' % (PATH.WORKDIR+'/'+'output.pbs/' + '${PBS_JOBID}')
          #       + ' -- ' + findpath('seisflows.system') +'/'+ 'wrappers/run ')
          args = ('-t 0-0 '
                 + findpath('seisflows.system') +'/'+ 'wrappers/run_torque ')
        return args


    def job_array_status(self, classname, method, jobs):
        """ Determines completion status of one or more jobs
        """

        isdone = False
        for job in jobs: #jobs variable contains only one job-id of the job-array 
            state = self._query(job)
	    #print 'job is: %s' % job
	    #print 'state is: %s' % state
            if state in ['R','Q']:
		isdone = False
	    else:
		# job-array is done if its id cannot be listed !NOT GOOD: TODO
		isdone = True
		
        return isdone, jobs


    def _query(self, jobid):
        """ Queries job state from PBS database
        """
        # TODO: replace shell utilities with native Python
        with open(PATH.SYSTEM+'/'+'job_status', 'w') as f:
            #call('qstat -x -tJ ' + jobid + ' | '
            call('qstat -t ' + jobid + ' | '
                + 'tail -n 1 ' + ' | '
                + 'awk \'{print $5}\'',
                stdout=f,stderr=open(os.devnull,'wb'))

        with open(PATH.SYSTEM+'/'+'job_status', 'r') as f:
            line = f.readline()
            state = line.strip()

        return state


    ### utility function

    def _timestamp(self):
        with open(PATH.SYSTEM+'/'+'timestamps', 'a') as f:
            line = time.strftime('%H:%M:%S')+'\n'
            f.write(line)

    def save_kwargs(self, classname, method, kwargs):
        kwargspath = join(PATH.OUTPUT, 'kwargs')
        kwargsfile = join(kwargspath, classname+'_'+method+'.p')
        unix.mkdir(kwargspath)
        saveobj(kwargsfile, kwargs)


