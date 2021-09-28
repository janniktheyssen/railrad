## This is an implementation of a 1D complex interpolation in cython
import numpy as np
from scipy.interpolate import interp1d


__all__ = ['Interp1d_complex', 'fn_shift', 'f0_shift']

class Interp1d_complex():
    """
    Wrapper around scipy.interpolate.interp1d class to enable 
    efficient complex number interpolation
    """
    def __init__(self, x, y, kind='linear', axis=-1,
                 copy=True, bounds_error=None, fill_value=np.nan,
                 assume_sorted=False):
        self.realint = interp1d(x, y.real, kind, axis, copy, bounds_error, fill_value, assume_sorted)
        self.imagint = interp1d(x, y.imag, kind, axis, copy, bounds_error, fill_value, assume_sorted)
    
    def __call__(self, ynew):
        realnew = self.realint(ynew)
        imagnew = self.imagint(ynew)
        return self.realint(ynew) + 1j * self.imagint(ynew)


def fn_shift(kn, k0, f0):
    return np.sqrt(((kn)**2 - (k0)**2) * 343**2 / ((2*np.pi)**2) + f0**2)


def f0_shift(k, k0, fn):
    return np.nan_to_num(np.sqrt(fn**2 - (k**2 - (k0)**2) * 343**2 / ((2*np.pi)**2)), copy=False, nan=-1)
