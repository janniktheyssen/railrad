# RailRad - calculate the acoustic radiation from railway track using pre-calculated transfer functions

A toolbox to evaluate the acoustic radiation from railway tracks
at a set of receiver points via pre-calculated transfer functions.
The calculation requires information about the surface normal velocities in 
frequency and wavenumber domain beforehand (e.g., evaluated with a Waveguide Finite Element model).


## The Database Class

Create a Class object to manage access to and processing of a database of pre-calculated transfer functions via 
    
    Database(path)

and where `path` is the path to a RailRad database. 
Provide the desired frequency and wavenumber discretisation and the desired source and receiver node
indices in

    Database.setup(f, k, receiver_nodes=[], source_nodes=[])

where the empty list `[]` can be used to indicate that all sources and/or receivers in the database
should be used.
Now the relevant acoustic transfer functions for the given frequency- and wavenumber discretisation
and the specified source and receiver nodes can be generated and stored in a variable by 
                            

    Database.return_tfs()

These transfer functions, multiplied with the structural surface velocity at the source nodes can 
then be superposed to generate the total sound pressure at the receiver points.
Alternatively, the surface normal velocity at the source nodes can be provided in 

    Database.superpose(Vn)

and the sound pressure at the receiver nodes is calculated automatically by multiplication and superposition. 
Vn must be a four-dimensional array of the the shape `n_f x n_k x n_in x n_source`
where `n_f` is the number of frequency bins in the spectrum,
      `n_k` is the number of wavenumbers at each frequency line,
      `n_in` can be different load cases, e.g. vertical and lateral load or different nodes, and
      `n_source` should be equivalent to the number of source nodes in the database.

The method

    Database.save_to_mat(filepath)

saves the entire database to a .mat (MATLAB-compatible) file at the given filename/-path.
The function 

    load_from_mat(filename)

then reads a previously saved database file from the .mat file.


## The geometries

The acoustic transfer functions have as of now been pre-calculated for four geometries. Each of the geometries are described by their source nodes and receiver nodes. The location and index of each node is displayed in the associated figures.

1. A free rail [![free rail - free field](docs/figures/free-rail_free-field_nodes.pdf)](docs/figures/free-rail_free-field_nodes.html)



