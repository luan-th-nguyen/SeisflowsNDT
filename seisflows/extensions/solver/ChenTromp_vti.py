from seisflows.tools.config import loadclass, ParameterObj

PAR = ParameterObj('SeisflowsParameters')
PATH = ParameterObj('SeisflowsPaths')


class ChenTromp_vti(loadclass('extensions.solver', 'specfem3d_legacy')):
    # data channels
    channels = []
    channels += ['x']

    # model parameters expected by solver
    model_parameters = []
    model_parameters += ['rho']
    model_parameters += ['A']
    model_parameters += ['C']
    model_parameters += ['L']
    model_parameters += ['N']
    model_parameters += ['F']
    model_parameters += ['Jc']
    model_parameters += ['Js']
    model_parameters += ['Kc']
    model_parameters += ['Ks']
    model_parameters += ['Mc']
    model_parameters += ['Ms']
    model_parameters += ['Gc']
    model_parameters += ['Gs']
    model_parameters += ['Bc']
    model_parameters += ['Bs']
    model_parameters += ['Hc']
    model_parameters += ['Hs']
    model_parameters += ['Dc']
    model_parameters += ['Ds']
    model_parameters += ['Ec']
    model_parameters += ['Es']

    # model parameters included in inversion
    inversion_parameters = []
    inversion_parameters += ['A']
    inversion_parameters += ['C']
    inversion_parameters += ['L']
    inversion_parameters += ['N']
    inversion_parameters += ['F']

    kernel_map = {
        'rho': 'rho_kernel',
        'A': 'A_kernel',
        'C': 'C_kernel',
        'N': 'N_kernel',
        'L': 'L_kernel',
        'F': 'F_kernel',
        'Jc': 'Jc_kernel',
        'Js': 'Js_kernel',
        'Kc': 'Kc_kernel',
        'Ks': 'Ks_kernel',
        'Mc': 'Mc_kernel',
        'Ms': 'Ms_kernel',
        'Gc': 'Gc_kernel',
        'Gs': 'Gs_kernel',
        'Bc': 'Bc_kernel',
        'Bs': 'Bs_kernel',
        'Hc': 'Hc_kernel',
        'Hs': 'Hs_kernel',
        'Dc': 'Dc_kernel',
        'Ds': 'Ds_kernel',
        'Ec': 'Ec_kernel',
        'Es': 'Es_kernel'}

