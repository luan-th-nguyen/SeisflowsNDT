
WORKFLOW='inversion'    # inversion, migration
SOLVER='specfem2d_ndt'      # specfem2d, specfem3d
SYSTEM='pbs_torque_lg'  # serial, pbs, slurm
PBSARGS='-q medium'      # PBS arguments
MEMORY=1
NODESIZE=24
NODES=1
MPIEXEC='mpirun'

OPTIMIZE='LBFGS'        # NLCG, LBFGS
PREPROCESS='base'       # base
POSTPROCESS='base'      # base

MISFIT='Waveform'
MATERIALS='Elastic'
DENSITY='Constant'


# WORKFLOW
BEGIN=1                 # first iteration
END=1                   # last iteration
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
NTASK= 5 #5             # must satisfy 1 <= NTASK <= NSRC
NPROC=4                 # processors per task
TASKTIME=10
WALLTIME=360
