
WORKFLOW='inversion'    # inversion, migration
SOLVER='specfem2d'      # specfem2d, specfem3d
SYSTEM='pbs_torque_lg'  # serial, pbs, slurm
PBSARGS='-q medium'      # PBS arguments
MEMORY=16
NODESIZE=24
#ENVIRONS='PBSDEBUG=yes'
MPIEXEC='/opt/openmpi/1.8.4/intel/bin/mpirun'

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
MUTE=0                  # mute direct arrival
FREQLO=0.               # low frequency corner
FREQHI=0.               # high frequency corner
MUTECONST=0.            # mute constant
MUTESLOPE=0.            # mute slope


# POSTPROCESSING
SMOOTH=30.              # smoothing radius
SCALE=6.0e6             # scaling factor


# OPTIMIZATION
PRECOND=None            # preconditioner type
STEPMAX=10              # maximum trial steps
STEPTHRESH=0.1          # step length safeguard


# SOLVER
NT=4800                 # number of time steps
DT=0.06                 # time step
F0=0.084                # dominant frequency


# SYSTEM
NTASK= 2 #5                # must satisfy 1 <= NTASK <= NSRC
NPROC=4                 # processors per task
WALLTIME=360
