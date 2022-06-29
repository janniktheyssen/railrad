# RailRad - calculate the acoustic radiation from railway track using pre-calculated transfer functions

A toolbox to evaluate the acoustic radiation from railway tracks
at a set of receiver points via pre-calculated transfer functions.
The calculation requires information about the surface normal velocities in 
frequency and wavenumber domain beforehand (e.g., evaluated with a Waveguide Finite Element model or an analytical rail model).
The total complex sound pressure in a receiver point can be found by multiplication of the track surface velocity with the corresponding acoustic transfer function and subsequent addition of the complex pressures.

## The Database class

Create a Class object to manage access to and processing of a database of pre-calculated transfer functions via 
    
    DB = Database(path)

and where `path` is the path to a RailRad database. 
Provide the desired frequency and wavenumber discretisation and the desired source and receiver node
indices in

    DB.setup(f, k, receiver_nodes=[0,1,2], source_nodes=range(91))

where the empty list `[]` can be used to indicate that all sources and/or receivers in the database
should be used (see [below](#the-geometries) for a description of source- and receiver positions and indices).
The variable `f` is a 1D array of frequencies (size `n_f`)  and `k` should be a matrix of size `n_f x n_k` containing an array of wavenumbers at each frequency.
Now the relevant acoustic transfer functions for the given frequency- and wavenumber discretisation
and the specified source and receiver nodes can be generated and stored in a variable by                             

    DB.return_tfs()

These transfer functions, multiplied with the structural surface velocity at the source nodes can 
then be superposed to generate the total sound pressure at the receiver points.
If the matrix becomes too large to handle in memory, it can instead be written to a temporary file by

    DB.tfs_to_hdf5(self, filename, f_index=[], k_index=[], receiver_nodes=[], source_nodes=[])

from where it can then be read frequency-by-frequency.

For small enough problems, the surface normal velocity at the source nodes can be directly provided in 

    DB.superpose(Vn)

and the sound pressure at the receiver nodes is calculated automatically by multiplication and superposition. 
Vn must be a four-dimensional array of the the shape `n_f x n_k x n_in x n_source`
where `n_f` is the number of frequency bins in the spectrum,
      `n_k` is the number of wavenumbers at each frequency line,
      `n_in` can be different load cases, e.g. vertical and lateral load or different nodes, and
      `n_source` should be equivalent to the number of source nodes in the database.

## Exporting to MATLAB

The method

    DB.save_to_mat(filepath)

saves the entire database to a .mat (MATLAB-compatible) file at the given filename/-path.
The function 

    load_from_mat(filename)

reads a previously saved database file from the .mat file.


## The geometries

The acoustic transfer functions have as of now been pre-calculated for four geometries. Each of the geometries are described by their source nodes and receiver nodes.

1. A UIC60 rail geometry in an acoustic free field,
2. A UIC60 rail geometry in an acoustic half-space with an acoustically hard boundary condition 5 cm below the foot of the rail,
3. A UIC60 rail with 5 cm distance to the top of a flat track surface,
4. A UIC60 rail with 5 cm distance to the top of a flat track surface and below an approximated hull of a passenger train.

The best way to explore these geometries is to create a database and plot the source and receiver nodes as shown [in this notebook](doc/figures/Railrad_demonstration.ipynb).