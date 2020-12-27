import unittest
import os
import numpy as np
import matplotlib.pyplot as plt
from obspy.core import Stream, Stats, Trace
from seisflows.tools import dispersion


class TestDispersionCode(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_load(self):
        cwd = os.getcwd()
        path = os.path.join(cwd, 'setup/test_dispersion/guided_waves_pipe/data_L01/')
        #print 'path: ', path
        NR = 24
        nt = 2000 # 6000
        u = TestDispersionCode.read_ascii(path, NR, nt)
        self.assertTrue(type(u), Stream)
        return u, NR, nt


    def test_get_dispersion(self):
        u, NR, nt = self.test_load()
        dt = 3.5e-5
        dx = 10.0
        cmin = 50.
        cmax = 8000.0
        dc = 10.
        fmax = 600.0
        f,c,img,fmax_idx,U,t = dispersion.get_dispersion(u,dx,cmin,cmax,dc,fmax)

        im, ax = plt.subplots(figsize=(7.0,5.0))
        ax.imshow(img[:,:],aspect='auto',origin='lower',extent=(f[0],f[fmax_idx],c[0],c[-1]),interpolation='bilinear')
        ax.set_xlabel('Frequency [kHz]', fontsize=14)
        ax.set_ylabel('Phase velocity [m/s]', fontsize=14)
        ax.tick_params(axis = 'both', which = 'major', labelsize = 14)
        ax.tick_params(axis = 'both', which = 'minor', labelsize = 14)
        cwd = os.getcwd()
        path = os.path.join(cwd, 'setup/test_dispersion/guided_waves_pipe/data_L01/')
        im.savefig(os.path.join(path, 'pipe_syn_dispersion_curves_L01.png'),dpi=300)

        self.assertEqual(fmax_idx, 41)


    @staticmethod
    def read_ascii(path, NR, nt):
        dat_type = 'semd'
        comp1 = 'FXX'
        comp2 = 'FXY'
        stream = Stream()
        for rec_x in range(0,NR):
            file_name_in1 = path + 'P.R' + str(int(rec_x+1)) + '.' + comp1 + '.' + dat_type
            file_name_in2 = path + 'P.R' + str(int(rec_x+1)) + '.' + comp2 + '.' + dat_type
            xz1 = np.genfromtxt(file_name_in1)
            xz2 = np.genfromtxt(file_name_in2)
            deg = 0.0
            alpha = np.arctan(xz2[:nt,1]/(1.0e-40 + xz1[:nt,1])) # angle of projection
            direction = np.sign(np.cos(deg*np.pi/180.0)*xz1[:nt,1]*np.cos(alpha) + np.sin(deg*np.pi/180.0)*xz2[:nt,1]*np.cos(alpha))    
            data = direction*np.sqrt(xz1[:nt,1]**2 + xz2[:nt,1]**2)*np.cos(alpha) # scalar radial component

            stats = Stats()
            stats.filename = path + 'P.R' + str(int(rec_x+1))
            stats.starttime = xz1[0,0]
            stats.delta = xz1[1,0] - xz1[0,0]
            stats.npts = len(xz1[:nt,0])

            try:
                parts = filename.split('.')
                stats.network = parts[0]
                stats.station = parts[1]
                stats.channel = temp[2]
            except:
                pass

            stream.append(Trace(data=data[:], header=stats))

        return stream


if __name__ == '__main__':
    unittest.main()

