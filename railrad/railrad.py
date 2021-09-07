from h5py import File
import numpy as np
from .helpers import *

# __all__ = ['Database']

class Database():
    def __init__(self, filepath ='.'):
        """
        path to the directory where the database files are stored
        """
        self.filepath = filepath

        if self.load_data():
            print('Successfully loaded the database.')

    def load_data(self):
        fh = File(self.filepath, 'r')
        self._tf_base = fh['tfs']
        self._f_base = fh['info/f'][()]
        self.k0 = fh['info/k0'][()]
        self.surf_coords = fh['info/coordinates'][()]
        self.normal_vectors = fh['info/normal_vectors'][()]
        self.fp_coords = fh['info/fp_coordinates'][()]
        self._source_nodes = fh['info/source_nodes'][()]  # these are the nodes available in the database
        self._receiver_nodes = np.arange(len(self.fp_coords))
        return True

    def setup(self, f, k, receiver_nodes=[], source_nodes=[]):
        """
        Set up the superposition

        f - frequency vector
        k - wavenumber matrix of size n_f x n_k with one wavenumber vector for each frequency line
        receiver_nodes - the nodes in the database at which 
                         the superposition should be evaluated.
        source_nodes - some source nodes can be excluded from the superposition.
                       These are assumed to have velocity 0.
        """
        self.source_nodes = (source_nodes if source_nodes != [] else self._source_nodes)  # these are the user's desired nodes
        self.receiver_nodes = (receiver_nodes if receiver_nodes != [] else self._receiver_nodes)
        self._check_nodes()
        self._nrn = len(self.receiver_nodes)
        self._nsn = len(self.source_nodes)
        self.f = f
        self.k = k
        self._check_f_range()
        self._nf = len(f)

        # self.tf = np.zeros((self._nrn, self._nsn, self._nf), dtype=complex)
        # for re_i, re in enumerate(self.receiver_nodes):
            # for so_i, so in enumerate(self.source_nodes):
                # self.tf[re_i, so_i] = interp_complex(self.f, self._f_base, self._tf_base[re_i, so_i], left=0)

    def superpose(self, Vn):
        """
        Superpose acoustic transfer functions with surface normal velocities
        by summing over the source nodes

        Vn has the shape n_f x n_k x n_in x n_source
            where n_f is the number of frequency bins in the spectrum
                  n_k is the number of wavenumbers at each frequency line,
                  n_in can be different load cases, e.g. vertical and lateral load or different nodes
                  n_source should be equivalent to the number of source nodes in the database
        """
        f = Interp1d_complex(self._f_base[()], 
                             self._tf_base[self.receiver_nodes][:, self.source_nodes],
                             assume_sorted=True, copy=False, fill_value=0, bounds_error=False)
        self.response = np.zeros((Vn.shape[0], Vn.shape[1], Vn.shape[2], self._nrn), dtype=complex)
        for fi, freq in enumerate(self.f):
            jomega = (1j * 2 * np.pi * freq)**2
            for ki, k in enumerate(self.k[fi]):
                f0 = f0_shift(k, self.k0, freq)
                r = f(f0)  # receiver_nodes, source_nodes
        #         response[fi, ki, :, :] = np.einsum('rs -> sr', r) * jomega
                self.response[fi, ki, :, :] = np.einsum('is, rs -> ir', Vn[fi, ki], r) * jomega


    def _check_f_range(self):
        if min(self.f) < min(self._f_base):
            print('Minimum f is smaller than the smallest f in the database. Results may be inaccurate.')
        if max(self.f) > max(self._f_base):
            print('Maximum f is larger than the largest f in the database. Results may be inaccurate.')

    def _check_nodes(self):
        if self.source_nodes != []:
            assert all([i in self._source_nodes for i in self.source_nodes]), \
            'At least one source node not in database.'
        else: 
            print('   Selected all source nodes in the database.')

        if self.receiver_nodes != []:
            assert all([i in range(len(self.fp_coords)) for i in self.receiver_nodes]), \
            'At least one receiver node exceeds the number of receiver nodes in the database.'
        else:
            print('   Selected all receiver nodes in the database.')


# def load_fp_data(nznodes, field_points):
#     nfp = len(field_points)
#     data_shape = File('../TFs_flat_slab/node_' + str(nznodes[0]) + '_p_fp.hdf5', 'r')['field_pressure'].shape
#     data = np.zeros((len(nznodes), data_shape[0], data_shape[1], data_shape[2], nfp), dtype=complex)
#     for node in range(len(nznodes)):
#         data[node] = File('../TFs_flat_slab/node_' + str(nznodes[node]) + '_p_fp.hdf5', 'r')['field_pressure'][..., field_points]
#     return data

# def prep_rail_acoustic_TFs_surf(nznodes, frequencies, data):
#     """
#     reads each rail acoustic TF from database
#     combines them in a matrix for the desired field points
#     """
#     nnznodes = nznodes.shape[0]
# #     nsp = 1628
#     nsp = 64
#     # extact the transfer function for one node in both directions,
#     # interpolate in frequency to match frequency vector of solver
#     freq_db = np.arange(0, 7500, 0.5)
#     nf_db = freq_db.shape[0]
#     nf = frequencies.shape[0]

#     tf = np.zeros((nf, 2, nnznodes, nsp), dtype=complex)
#     for node in range(nnznodes):
#         file_handle = data[node]
#         print('reading acoustic tf from database for node ', nznodes[node])
#         for diri in [0, 1]:
#             for sp in range(nsp): 
# #                 if (sp % 500 == 0):
# #                     print("interpolating at surface_point "+str(sp))
#                 sp_interp = interp_complex(frequencies, freq_db, file_handle[:, 0, diri, sp], left=None)
#                 tf[:, diri, node, sp] = sp_interp
#     return tf
