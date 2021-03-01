
import sys
import os
import numpy as np
import obspy

from seisflows.tools import msg, unix
from seisflows.tools.tools import exists, getset
from seisflows.config import ParameterError

from seisflows.plugins import adjoint, misfit, readers, writers
from seisflows.tools import signal
from seisflows.tools.seismic import write_source_specfem2d, write_stations_specfem2d

PAR = sys.modules['seisflows_parameters']
PATH = sys.modules['seisflows_paths']


class base(object):
    """ Data preprocessing class
    """

    def check(self):
        """ Checks parameters and paths
        """
        # usedf for inversion
        if 'MISFIT' not in PAR:
            setattr(PAR, 'MISFIT', None)

        # used for migration
        if 'BACKPROJECT' not in PAR:
            setattr(PAR, 'BACKPROJECT', None)

        # data file format
        if 'FORMAT' not in PAR:
            raise ParameterError(PAR, 'FORMAT')

        # data normalization option
        if 'NORMALIZE' not in PAR:
            setattr(PAR, 'NORMALIZE', None)

        # data muting option
        if 'MUTE' not in PAR:
            setattr(PAR, 'MUTE', None)

        # data filtering option
        if 'FILTER' not in PAR:
            setattr(PAR, 'FILTER', None)


        # assertions
        if PAR.FORMAT not in dir(readers):
            print(msg.ReaderError)
            raise ParameterError()

        if PAR.FORMAT not in dir(writers):
            print(msg.WriterError)
            raise ParameterError()

        self.check_filter()
        self.check_mute()
        self.check_normalize()


    def setup(self):
        """ Sets up data preprocessing machinery
        """
        # define misfit function and adjoint trace generator
        if PAR.MISFIT:
            self.misfit = getattr(misfit, PAR.MISFIT)
            self.adjoint = getattr(adjoint, PAR.MISFIT)
        elif PAR.BACKPROJECT:
            self.adjoint = getattr(adjoint, PAR.BACKPROJECT)

        # define seismic data reader and writer
        self.reader = getattr(readers, PAR.FORMAT)
        self.writer = getattr(writers, PAR.FORMAT)


    def prepare_eval_grad(self, path='.'):
        """ Prepares solver for gradient evaluation by writing residuals and
          adjoint traces

          INPUT
            PATH - directory containing observed and synthetic seismic data
        """
        solver = sys.modules['seisflows_solver']

        for filename in solver.data_filenames:
            obs = self.reader(path+'/'+'traces/obs', filename)
            syn = self.reader(path+'/'+'traces/syn', filename)

            # process observations
            obs = self.apply_filter(obs)
            obs = self.apply_mute(obs)
            obs = self.apply_normalize(obs)

            # process synthetics
            syn = self.apply_filter(syn)
            syn = self.apply_mute(syn)
            syn = self.apply_normalize(syn)

            if PAR.MISFIT:
                self.write_residuals(path, syn, obs)

            filename = filename.replace('_d.su', '.su')    # names of adjoint traces are without '_d'
            self.write_adjoint_traces(path+'/'+'traces/adj', syn, obs, filename)


    def write_residuals(self, path, syn, obs):
        """ Computes residuals from observations and synthetics

          INPUT
            PATH - location residuals will be written
            SYN - obspy Stream object containing synthetic data
            OBS - obspy Stream object containing observed data
        """
        nt, dt, _ = self.get_time_scheme(syn)
        nn, _ = self.get_network_size(syn)

        residuals = []
        for ii in range(nn):
            residuals.append(self.misfit(syn[ii].data, obs[ii].data, nt, dt))

        filename = path+'/'+'residuals'
        if exists(filename):
            residuals.extend(list(np.loadtxt(filename)))

        np.savetxt(filename, residuals)


    def sum_residuals(self, files):
        """ Sums squares of residuals

          INPUT
            FILES - files containing residuals
        """
        total_misfit = 0.
        for file in files:
            total_misfit += np.sum(np.loadtxt(file)**2.)
        return total_misfit
        

    def write_adjoint_traces(self, path, syn, obs, channel):
        """ Writes "adjoint traces" required for gradient computation
         (overwrites synthetic data in the process)

          INPUT
            PATH - location "adjoint traces" will be written
            SYN - obspy Stream object containing synthetic data
            OBS - obspy Stream object containing observed data
            CHANNEL - channel or component code used by writer
        """
        nt, dt, _ = self.get_time_scheme(syn)
        nn, _ = self.get_network_size(syn)

        adj = syn
        for ii in range(nn):
            adj[ii].data = self.adjoint(syn[ii].data, obs[ii].data, nt, dt)

        self.writer(adj, path, channel)


    def write_obs_as_sources(self, path, path_out, obs, channel):
        """ Writes observed traces as source for time reversed simulation
          INPUT
            PATH - location time reversed observed traces will be written
            OBS - obspy Stream object containing "time reversed" observed data
            CHANNEL - channel or component code used by writer
        """
        nt, dt, _ = self.get_time_scheme(obs)
        nn, _ = self.get_network_size(obs)

        writer_ascii = getattr(writers, 'ascii_2')

        writer_ascii(obs, path_out, channel, dt)
        source_files = [path_out + '/' + channel + str(ir).zfill(4) for ir in range(len(obs))]

        r_coords_x, r_coords_y, _ = self.get_receiver_coords(obs)
        s_coords_x, s_coords_y, _ = self.get_source_coords(obs)
        write_source_specfem2d(r_coords_x, r_coords_y, PAR.F0, source_files, source_type=1, stf_type=8, path=path)
        write_stations_specfem2d([s_coords_x[0]], [s_coords_y[0]], path=path)   # single station


    ### signal processing

    def apply_filter(self, traces):
        if not PAR.FILTER:
            return traces

        elif PAR.FILTER == 'Bandpass':
            for tr in traces:
                tr.detrend('demean')
                tr.detrend('linear')
                tr.taper(0.05, type='hann')
                tr.filter('bandpass', freqmin=PAR.FREQMIN, freqmax=PAR.FREQMAX)

        elif PAR.FILTER == 'Lowpass':
            for tr in traces:
                tr.detrend('demean')
                tr.detrend('linear')
                tr.taper(0.05, type='hann')
                tr.filter('lowpass', freq=PAR.FREQ)

        elif PAR.FILTER == 'Highpass':
            for tr in traces:
                tr.detrend('demean')
                tr.detrend('linear')
                tr.taper(0.05, type='hann')
                tr.filter('highpass', freq=PAR.FREQ)

        else:
            raise ParameterError()

        return traces


    def apply_mute(self, traces):
        if not PAR.MUTE:
            return traces

        if 'MuteEarlyArrivals' in PAR.MUTE:
            traces = signal.mute_early_arrivals(traces,
                PAR.MUTE_EARLY_ARRIVALS_SLOPE, # (units: time/distance)
                PAR.MUTE_EARLY_ARRIVALS_CONST, # (units: time)
                self.get_time_scheme(traces),
                self.get_source_coords(traces),
                self.get_receiver_coords(traces))

        if 'MuteLateArrivals' in PAR.MUTE:
            traces = signal.mute_late_arrivals(traces,
                PAR.MUTE_LATE_ARRIVALS_SLOPE, # (units: time/distance)
                PAR.MUTE_LATE_ARRIVALS_CONST, # (units: time)
                self.get_time_scheme(traces),
                self.get_source_coords(traces),
                self.get_receiver_coords(traces))

        if 'MuteShortOffsets' in PAR.MUTE:
            traces = signal.mute_short_offsets(traces,
                PAR.MUTE_SHORT_OFFSETS_DIST,
                self.get_source_coords(traces),
                self.get_receiver_coords(traces))

        if 'MuteLongOffsets' in PAR.MUTE:
            traces = signal.mute_long_offsets(traces,
                PAR.MUTE_LONG_OFFSETS_DIST,
                self.get_source_coords(traces),
                self.get_receiver_coords(traces))

        return traces


    def apply_normalize(self, traces):
        if not PAR.NORMALIZE:
            return traces

        if 'NormalizeEventsL1' in PAR.NORMALIZE:
            # normalize event by L1 norm of all traces
            w = 0.
            for tr in traces:
                w += np.linalg.norm(tr.data, ord=1)
            for tr in traces:
                tr.data /= w

        elif 'NormalizeEventsL2' in PAR.NORMALIZE:
            # normalize event by L2 norm of all traces
            w = 0.
            for tr in traces:
                w += np.linalg.norm(tr.data, ord=2)
            for tr in traces:
                tr.data /= w

        if 'NormalizeTracesL1' in PAR.NORMALIZE:
            # normalize each trace by its L1 norm
            for tr in traces:
                w = np.linalg.norm(tr.data, ord=1)
                if w > 0:
                    tr.data /= w

        elif 'NormalizeTracesL2' in PAR.NORMALIZE:
            # normalize each trace by its L2 norm
            for tr in traces:
                w = np.linalg.norm(tr.data, ord=2)
                if w > 0:
                    tr.data /= w

        return traces


    def apply_filter_backwards(self, traces):
        for tr in traces:
            tr.data = np.flip(tr.data, 0)

        traces = self.apply_filter(traces)

        for tr in traces:
            tr.data = np.flip(tr.data, 0)

        return traces


    def revert_time(self, traces):
        for tr in traces:
            tr.data = np.flip(tr.data, 0)
        
        return traces


    def prepare_eval_source(self, path='.'):
        """ Prepares sources for forward simulation
        Used in case the estimation of source time function is needed
          INPUT
            PATH - directory containing observed data
        """
        solver = sys.modules['seisflows_solver']
        path_out = path+'/'+'DATA/traces_obs_tr'
        if not os.path.exists(path_out):
            os.makedirs(path_out)

        for filename in solver.data_filenames:
            obs = self.reader(path+'/'+'traces/obs', filename)
            obs = self.revert_time(obs)

            # process observations
            obs = self.apply_filter(obs)
            obs = self.apply_mute(obs)
            obs = self.apply_normalize(obs)

            self.write_obs_as_sources(path, path_out, obs, filename)


    def set_eval_source(self, path='.'):
        """ Uses the estimated source time function
        """
        solver = sys.modules['seisflows_solver']
        path_out = path+'/'+'DATA/estimated_stf'
        if not os.path.exists(path_out):
            os.makedirs(path_out)

        for filename in solver.data_filenames:
            syn = self.reader(path+'/'+'traces/syn', filename)  # estimated source time
            syn = self.revert_time(syn)

            self.write_obs_as_sources(path, path_out, syn, filename)


    def reset_eval_stations(self, path='.'):
        """ Resets (single) source for forward/ adjoint simulation
        """
        solver = sys.modules['seisflows_solver']

        for filename in solver.data_filenames:
            obs = self.reader(path+'/'+'traces/obs', filename)

            #s_coords_x, s_coords_y, _ = self.get_source_coords(obs)
            #x, y = [s_coords_x[0]], [s_coords_y[0]]    # single source
            #write_source_specfem2d(x, y, PAR.F0, ['\"\"'], source_type=1, stf_type=1, path=path)
            r_coords_x, r_coords_y, _ = self.get_receiver_coords(obs)   # single source
            write_stations_specfem2d(r_coords_x, r_coords_y, path)   # full stations

    ### additional parameter checking

    def check_filter(self):
        """ Checks filter settings
        """
        assert getset(PAR.FILTER) < set([
            'Bandpass',
            'Lowpass',
            'Highpass'])

        if PAR.FILTER == 'Bandpass':
            if 'FREQMIN' not in PAR: raise ParameterError('FREQMIN')
            if 'FREQMAX' not in PAR: raise ParameterError('FREQMAX')
            assert 0 < PAR.FREQMIN
            assert PAR.FREQMIN < PAR.FREQMAX
            assert PAR.FREQMAX < np.inf

        elif PAR.FILTER == 'Lowpass':
            raise NotImplementedError
            if 'FREQ' not in PAR: raise ParameterError('FREQ')
            assert 0 < PAR.FREQ <= np.inf

        elif PAR.FILTER == 'Highpass':
            raise NotImplementedError
            if 'FREQ' not in PAR: raise ParameterError('FREQ')
            assert 0 <= PAR.FREQ < np.inf



    def check_mute(self):
        """ Checks mute settings
        """
        if not PAR.MUTE:
            return

        assert getset(PAR.MUTE) <= set([
            'MuteEarlyArrivals',
            'MuteLateArrivals',
            'MuteShortOffsets',
            'MuteLongOffsets'])

        if 'MuteEarlyArrivals' in PAR.MUTE:
            assert 'MUTE_EARLY_ARRIVALS_SLOPE' in PAR
            assert 'MUTE_EARLY_ARRIVALS_CONST' in PAR
            assert PAR.MUTE_EARLY_ARRIVALS_SLOPE >= 0.

        if 'MuteLateArrivals' in PAR.MUTE:
            assert 'MUTE_LATE_ARRIVALS_SLOPE' in PAR
            assert 'MUTE_LATE_ARRIVALS_CONST' in PAR
            assert PAR.MUTE_LATE_ARRIVALS_SLOPE >= 0.

        if 'MuteShortOffsets' in PAR.MUTE:
            assert 'MUTE_SHORT_OFFSETS_DIST' in PAR
            assert 0 < PAR.MUTE_SHORT_OFFSETS_DIST

        if 'MuteLongOffsets' in PAR.MUTE:
            assert 'MUTE_LONG_OFFSETS_DIST' in PAR
            assert 0 < PAR.MUTE_SHORT_OFFSETS_DIST

        if 'MuteShortOffsets' not in PAR.MUTE:
            setattr(PAR, 'MUTE_SHORT_OFFSETS_DIST', 0.)

        if 'MuteLongOffsets' not in PAR.MUTE:
            setattr(PAR, 'MUTE_LONG_OFFSETS_DIST', 0.)


    def check_normalize(self):
        assert getset(PAR.NORMALIZE) < set([
            'NormalizeTracesL1',
            'NormalizeTracesL2',
            'NormalizeEventsL1',
            'NormalizeEventsL2'])


    ### utility functions

    def get_time_scheme(self, traces):
        # FIXME: extract time scheme from trace headers rather than parameters file
        nt = PAR.NT
        dt = PAR.DT
        t0 = 0.
        return nt, dt, t0


    def get_network_size(self, traces):
        nrec = len(traces)
        nsrc = 1
        return nrec, nsrc


    def get_receiver_coords(self, traces):
        if PAR.FORMAT in ['SU', 'su']:
            rx = []
            ry = []
            rz = []
            for trace in traces:
                rx += [trace.stats.su.trace_header.group_coordinate_x]
                ry += [trace.stats.su.trace_header.group_coordinate_y]
                rz += [0.]
            return rx, ry, rz

        else:
             raise NotImplementedError


    def get_source_coords(self, traces):
        if PAR.FORMAT in ['SU', 'su']:
            sx = []
            sy = []
            sz = []
            for trace in traces:
                sx += [trace.stats.su.trace_header.source_coordinate_x]
                sy += [trace.stats.su.trace_header.source_coordinate_y]
                sz += [0.]
            return sx, sy, sz

        else:
             raise NotImplementedError


