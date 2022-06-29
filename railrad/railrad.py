from h5py import File
import numpy as np
from .helpers import *
from scipy.io import savemat, loadmat

__all__ = ['Database', 'load_from_mat']

class Database():
    def __init__(self, filepath ='.'):
        """
        path to the directory where the database files are stored
        """
        self.filepath = filepath

        if self.load_data():
            print('Successfully loaded the database.')

    def load_data(self):
        with File(self.filepath, 'r') as fh:
            self._tf_base = fh['tfs'][()]
            self._f_base = fh['info/f'][()]
            self.k0 = fh['info/k0'][()]
            self.source_coordinates = fh['info/source_coordinates'][()]
            self.normal_vectors = fh['info/normal_vectors'][()]
            self.receiver_coordinates = fh['info/receiver_coordinates'][()] 
            # these are the nodes available in the database:
            self._source_nodes = fh['info/source_nodes'][()]
            self._receiver_nodes = np.arange(len(self.receiver_coordinates))
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
        self._nk = k.shape[1]

    def superpose(self, Vn):
        """
        Superpose contributions from all source points to the complex pressures
        at receiver points by multiplication of the acoustic transfer functions
        with surface normal velocities and summing over the source nodes.

        Vn has the shape n_f x n_k x n_in x n_source
            where n_f is the number of frequency bins in the spectrum
                  n_k is the number of wavenumbers at each frequency line,
                  n_in can be different load cases, e.g. vertical and lateral load or different nodes
                  n_source should be equivalent to the number of source nodes in the database

        Store superposed complex pressure in a matrix at self.response
            which has the shape n_f x n_k x n_receiver

        """
        f = Interp1d_complex(self._f_base, 
                             self._tf_base[self.receiver_nodes][:, self.source_nodes],
                             assume_sorted=True, copy=False, fill_value=0, bounds_error=False)
        self.response = np.zeros((Vn.shape[0], Vn.shape[1], Vn.shape[2], self._nrn), dtype=complex)
        for fi, freq in enumerate(self.f):
            jomega = (1j * 2 * np.pi * freq)
            for ki, k in enumerate(self.k[fi]):
                f0 = f0_shift(k, self.k0, freq)
                r = f(f0)  # receiver_nodes, source_nodes
                self.response[fi, ki, :, :] = np.einsum('is, rs -> ir', Vn[fi, ki], r) * jomega

    def return_tfs(self, f_index=[], k_index=[], receiver_nodes=[], source_nodes=[]):
        """
        return the acoustic transfer functions

        tfs has the shape n_f x n_k x n_receiver x n_source
            where n_f is the number of frequency bins in the spectrum
                  n_k is the number of wavenumbers at each frequency line,
                  n_source should be equivalent to the number of source nodes in the database
                  n_receiver is the number of receiver points
        """
        if f_index == []:
            f_index = np.arange(self._nf)
        if k_index == []:
            k_index = np.arange(self._nk)
        if receiver_nodes == []:
            receiver_nodes = self.receiver_nodes
        if source_nodes == []:
            source_nodes = self.source_nodes

        f = Interp1d_complex(self._f_base, 
                             self._tf_base[receiver_nodes][:, source_nodes], kind='cubic',
                             assume_sorted=True, copy=False, fill_value=0, bounds_error=False)

        tfs = np.zeros((len(f_index), len(k_index), len(receiver_nodes), len(source_nodes)), dtype=complex)
        for fi, freq in enumerate(self.f[f_index]):
            jomega = (1j * 2 * np.pi * freq)
            for ki, k in enumerate(self.k[fi][k_index]):
                f0 = f0_shift(k, self.k0, freq)
                r = f(f0)  # receiver_nodes, source_nodes
                tfs[fi, ki, :, :] = r * jomega
        return tfs

    def tfs_to_hdf5(self, filename, f_index=[], k_index=[], receiver_nodes=[], source_nodes=[]):
        """
        As 'return_tfs', but store the acoustic transfer functions in a file, 
        writing one frequency line at once. Useful for large matrices and computers with
        limited working memory.

        tfs has the shape n_f x n_k x n_receiver x n_source
            where n_f is the number of frequency bins in the spectrum
                  n_k is the number of wavenumbers at each frequency line,
                  n_source should be equivalent to the number of source nodes in the database
                  n_receiver is the number of receiver points
        """
        if f_index == []:
            f_index = np.arange(self._nf)
        if k_index == []:
            k_index = np.arange(self._nk)
        if receiver_nodes == []:
            receiver_nodes = self.receiver_nodes
        if source_nodes == []:
            source_nodes = self.source_nodes

        f = Interp1d_complex(self._f_base, 
                             self._tf_base[receiver_nodes][:, source_nodes], kind='cubic',
                             assume_sorted=True, copy=False, fill_value=0, bounds_error=False)

        tfs = np.zeros((len(k_index), len(receiver_nodes), len(source_nodes)), dtype=complex)

        with File(filename, 'w') as file:
            dset = file.create_dataset('tfs', (len(f_index), len(k_index), len(receiver_nodes), len(source_nodes)), 
                                    dtype=complex, chunks=(1, len(k_index), len(receiver_nodes), len(source_nodes)))
            for fi, freq in enumerate(self.f[f_index]):
                jomega = (1j * 2 * np.pi * freq)
                for ki, k in enumerate(self.k[fi][k_index]):
                    f0 = f0_shift(k, self.k0, freq)
                    r = f(f0)  # receiver_nodes, source_nodes
                    tfs[ki] = r * jomega
                dset[fi] = tfs


    def save_to_mat(self, filename):
        """
        Save database to .mat file. Note that this might raise errors for 
        databases larger than 4 GB.
        """
        savemat(filename, {'db':self})

    def _check_f_range(self):
        """
        If the desired frequency range exceeds the pre-calculated frequency range in the database,
        the error in the interpolation is likely larger than desired. 
        This function checks if that is the case and prints a warning.
        """
        if min(self.f) < min(self._f_base):
            print('Minimum f is smaller than the smallest f in the database. Results may be inaccurate.')
        if max(self.f) > max(self._f_base):
            print('Maximum f is larger than the largest f in the database. Results may be inaccurate.')

    def _check_nodes(self):
        """
        Check if the specified source node indices are valid inputs.
        """
        if self.source_nodes != []:
            assert all([i in self._source_nodes for i in self.source_nodes]), \
            'At least one source node not in database.'
        else: 
            print('   Selected all source nodes in the database.')

        if self.receiver_nodes != []:
            assert all([i in range(len(self.receiver_coordinates)) for i in self.receiver_nodes]), \
            'At least one receiver node exceeds the number of receiver nodes in the database.'
        else:
            print('   Selected all receiver nodes in the database.')

def load_from_mat(filename):
    """
    Load a previously saved Database from a .mat file.
    """
    db_temp = _struct_to_dict(loadmat(filename)['db'])
    db = Database(db_temp['filepath'])
    db.__dict__.update(db_temp)
    return db
