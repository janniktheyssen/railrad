# RailRad - calculate the acoustic radiaton from railway track using pre-calculated transfer functions

A toolbox to evaluate the acoustic radiation from railway tracks
at a set of receiver points via pre-calculated transfer functions.
The calculation requires information about the surface normal velocities in 
frequency and wavenumber domain beforehand (e.g., evaluated with a Waveguide Finite Element model).


    Database(filepath) - read the database of either field points or surface points.

    Database.setup() - provide the desired frequency and wavenumber discretisation

    Database.superpose() - provide the surface normal velocity at the surface nodes.
                           The pressure at the desired output nodes is calculated via
                           superposition of the individual transfer functions from each 
                           source node, multiplied with the surface normal velocity,
                           to each receiver point.

