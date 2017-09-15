
WORKFLOW='inversion'    # inversion, migration
SOLVER='specfem2d_ndt'      # specfem2d, specfem3d
SYSTEM='pbs_torque_lg'  # serial, pbs, slurm
PBSARGS='-q medium'      # PBS arguments: '-q medium/big'
MEMORY=1
NODESIZE=24
NODES=1 # 2
MPIEXEC='mpirun'

OPTIMIZE='LBFGS'        # NLCG, LBFGS
PREPROCESS='base'       # base
POSTPROCESS='base'      # base

MISFIT='Waveform'
MATERIALS='Elastic'
DENSITY='Constant'


# WORKFLOW
BEGIN=1                 # first iteration
END=20                   # last iteration
NREC=10                 # number of receivers
NSRC=10                 # number of sources
SAVEGRADIENT=1          # save gradient how often
SAVERESIDUALS=1

# PREPROCESSING
FORMAT='su'             # data file format
CHANNELS='z'            # data channels
NORMALIZE=0             # normalize
MUTE='MuteEarlyArrivals'                 # mute direct arrival
MUTE_EARLY_ARRIVALS_CONST=5.0e-2 	# mute constant
MUTE_EARLY_ARRIVALS_SLOPE=0.		# mute slope
BANDPASS=0              # bandpass
FREQLO=0.               # low frequency corner
FREQHI=0.               # high frequency corner


# POSTPROCESSING
SMOOTH=30.              # smoothing radius
#SCALE=6.0e6             # scaling factor


# OPTIMIZATION
PRECOND=None            # preconditioner type
STEPMAX=10              # maximum trial steps
STEPTHRESH=0.1 #0.1          # step length safeguard


# SOLVER
NT=2200                 # number of time steps
DT=5.e-5                # time step
F0=40.                  # dominant frequency


# SYSTEM
NTASK= 5 #10             # must satisfy 1 <= NTASK <= NSRC
NPROC=4                 # processors per task
TASKTIME=10
WALLTIME=360
