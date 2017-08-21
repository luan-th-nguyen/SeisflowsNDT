
WORKFLOW='inversion'    # inversion, migration
SOLVER='specfem2d_devel'      # specfem2d, specfem3d
SYSTEM='multicore'  	# serial, pbs, slurm
NPROCMAX=48 #24
#MEMORY=16
#NODESIZE=24
#MPIEXEC='/opt/openmpi/1.8.4/intel/bin/mpirun'
MPIEXEC='mpirun'

OPTIMIZE='LBFGS'        # NLCG, LBFGS
PREPROCESS='base'       # base
POSTPROCESS='base'      # base

MISFIT='Waveform'
MATERIALS='Elastic'
DENSITY='Constant'


# WORKFLOW
BEGIN=1                 # first iteration
END=5                   # last iteration
NREC=10                 # number of receivers
NSRC=10                 # number of sources
SAVEGRADIENT=1          # save gradient how often
SAVERESIDUALS=1

# PREPROCESSING
FORMAT='su'             # data file format
CHANNELS='z'            # data channels
NORMALIZE=0             # normalize
BANDPASS=0              # bandpass
FREQLO=0.               # low frequency corner
FREQHI=0.               # high frequency corner
MUTE=0 #'MuteEarlyArrivals' # mute direct arrival
MUTECONST=5.0e-2        # mute constant
MUTESLOPE=0.            # mute slope

# POSTPROCESSING
SMOOTH=30.              # smoothing radius
#SCALE=6.0e6             # scaling factor


# OPTIMIZATION
PRECOND=None            # preconditioner type
STEPMAX=10              # maximum trial steps
STEPTHRESH=0.1          # step length safeguard


# SOLVER
NT=2200                 # number of time steps
DT=5.e-5                # time step
F0=40.                  # dominant frequency


# SYSTEM
NTASK= 10               # must satisfy 1 <= NTASK <= NSRC
NTASKMAX = 10# 5
NPROC=4                 # processors per task
WALLTIME=360
