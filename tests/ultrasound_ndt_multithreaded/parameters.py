WORKFLOW='inversion'    # inversion, migration
SOLVER='specfem2d'      # specfem2d, specfem3d
SYSTEM='multicore'         # serial, pbs, slurm
#SYSTEM='serial'         # serial, pbs, slurm
NPROCMAX=10		# for SYSTEM='multithreaded'
OPTIMIZE='LBFGS'         # base, newton
PREPROCESS='base'
POSTPROCESS='base'      # base

MISFIT='Waveform'
MATERIALS='Elastic'
DENSITY='Constant'


# WORKFLOW
BEGIN=1                 # first iteration
END=5                  # last iteration
NREC=10                 # number of receivers
NSRC=10                 # number of sources
SAVEGRADIENT=1          # save gradient how often
SAVERESIDUALS=1

# PREPROCESSING
FORMAT='su'             # data file format
CHANNELS='z'            # data channels
NORMALIZE=0             # normalize
BANDPASS=0              # bandpass
MUTE='MuteEarlyArrivals' #0 			# mute direct arrival
FREQLO=0.               # low frequency corner
FREQHI=0.               # high frequency corner
#MUTECONST=5.0e-2 #0.            # mute constant
#MUTESLOPE=0.            # mute slope
MUTE_EARLY_ARRIVALS_SLOPE = 5.0e-2
MUTE_EARLY_ARRIVALS_CONST = 0.
COMPENSATE='' 		#'Traveltime' # Compensation for later arrivals


# POSTPROCESSING
SMOOTH=30. #30.              # smoothing radius
#SCALE=6.0e6            # scaling factor


# OPTIMIZATION
PRECOND=None            # preconditioner type
STEPMAX=10              # maximum trial steps
STEPTHRESH=0.1 #0.03          # step length safeguard


# SOLVER
NT=2200 #2400                 # number of time steps
DT=5.e-5                # time step
F0=40.                  # dominant frequency


# SYSTEM
NTASK=10                # must satisfy 1 <= NTASK <= NSRC
NPROC=1                 # processors per task
WALLTIME=30
