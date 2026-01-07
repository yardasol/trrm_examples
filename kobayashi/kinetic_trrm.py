import openmc
import numpy as np

## Materials
source_mat = openmc.Material(name="source")
void_mat = openmc.Material(name="void")
shield_mat = openmc.Material(name="shield")
shield_mat.add_elements_from_formula('B4C')
shield_mat.set_density('g/cc', 2.50)

mats =  openmc.Materials([shield_mat])

## Geometry
source_cell = openmc.Cell(fill=source_mat, name='infinite source region')
void_cell = openmc.Cell(fill=shield_mat, name='infinite void region')
shield_cell = openmc.Cell(fill=shield_mat, name='infinite shield region')

su = openmc.Universe()
su.add_cells([source_cell])

vu = openmc.Universe()
vu.add_cells([void_cell])

au = openmc.Universe()
au.add_cells([shield_cell])

z_base = [
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [vu, vu, vu, vu, au, au],
        [vu, au, au, au, au, au],
        [vu, au, au, au, au, au],
        [vu, au, au, au, au, au],
        [vu, au, au, au, au, au],
        [su, au, au, au, au, au]
                     ]

z_col = [
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, vu, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au]
                     ]

z_high = [
        [au, au, au, vu, au, au],
        [au, au, au, vu, au, au],
        [au, au, au, vu, au, au],
        [au, au, au, vu, au, au],
        [au, au, au, vu, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au]
                     ]

z_cap = [
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au],
        [au, au, au, au, au, au]
                     ]

dogleg_pattern = [
        z_base,
        z_col,
        z_col,
        z_high,
        z_cap,
        z_cap
        ]

x = 60.0
x_dim = 6

y = 100.0
y_dim = 10

z = 60.0
z_dim = 6

lattice = openmc.RectLattice()
lattice.lower_left = [0.0, 0.0, 0.0]
lattice.pitch = [x/x_dim, y/y_dim, z/z_dim]
lattice.universes = dogleg_pattern

lattice_cell = openmc.Cell(fill=lattice)

lattice_uni = openmc.Universe()
lattice_uni.add_cells([lattice_cell])

x_low  = openmc.XPlane(x0=0.0,boundary_type='reflective') 
x_high = openmc.XPlane(x0=x,boundary_type='vacuum') 

y_low  = openmc.YPlane(y0=0.0,boundary_type='reflective') 
y_high = openmc.YPlane(y0=y,boundary_type='vacuum') 

z_low  = openmc.ZPlane(z0=0.0,boundary_type='reflective') 
z_high = openmc.ZPlane(z0=z,boundary_type='vacuum') 

full_domain = openmc.Cell(fill=lattice_uni, region=+x_low & -x_high & +y_low & -y_high & +z_low & -z_high, name='full domain')

root = openmc.Universe(name='root universe')
root.add_cell(full_domain)

# Create a geometry with the two cells and export to XML
geometry = openmc.Geometry(root)

###############################################################################
# Define problem settings

# Instantiate a Settings object, set all runtime parameters, and export to XML
settings = openmc.Settings()
settings.batches = 1600
#settings.inactive = 5
settings.particles = 1000000
settings.run_mode = 'fixed source'

#settings.random_ray_distance_active = 100.0
#settings.random_ray_distance_inactive = 20.0
#settings.solver_type = 'random ray'
#settings.run_mode = 'fixed source'

# Create an initial uniform spatial source for ray integration
#lower_left = (-pitch, -pitch, -1)
#upper_right = (pitch, pitch, 1)
#uniform_dist = openmc.stats.Box(lower_left, upper_right, only_fissionable=False)
#rr_source = openmc.IndependentSource(space=uniform_dist, particle="random_ray")

# Create the neutron source in the bottom right of the moderator
strengths = [1.0] # Good - fast group appears largest (besides most thermal)
midpoints = [100.0]
energy_distribution = openmc.stats.Discrete(x=midpoints,p=strengths)

lower_left_src = [0.0, 0.0, 0.0]
upper_right_src = [10.0, 10.0, 10.0]
spatial_distribution = openmc.stats.Box(lower_left_src, upper_right_src, only_fissionable=False)

#source = openmc.IndependentSource(energy=energy_distribution, domains=[source_mat], strength=2.0) # works
source = openmc.IndependentSource(space=spatial_distribution, energy=energy_distribution, constraints={
                                      'domains': [su]}, strength=1.0) # works

#settings.source = [source, rr_source]
settings.source = [source]
#settings.export_to_xml()

###############################################################################
# Define tallies

# Create a mesh that will be used for tallying
#mesh = openmc.RegularMesh()
#mesh.dimension = (x_dim, y_dim, z_dim)
#mesh.lower_left = (0.0, 0.0, 0.0)
#mesh.upper_right = (x, y, z)

# Create a mesh filter that can be used in a tally
#mesh_filter = openmc.MeshFilter(mesh)

# Now use the mesh filter in a tally and indicate what scores are desired
#tally = openmc.Tally(name="Mesh tally")
#tally.filters = [mesh_filter]
#tally.scores = ['flux']
#tally.estimator = 'collision'
#tally.estimator = 'analog'

estimator = 'tracklength'

# Case 3A
mesh_3A = openmc.RegularMesh()
mesh_3A.dimension = (1, y_dim, 1)
mesh_3A.lower_left = (0.0, 0.0, 0.0)
mesh_3A.upper_right = (10.0, y, 10.0)
mesh_filter_3A = openmc.MeshFilter(mesh_3A)

tally_3A = openmc.Tally(name="Case 3A")
tally_3A.filters = [mesh_filter_3A]
tally_3A.scores = ['flux']
tally_3A.estimator = estimator

# Case 3B
mesh_3B = openmc.RegularMesh()
mesh_3B.dimension = (x_dim, 1, 1)
mesh_3B.lower_left = (0.0, 50.0, 0.0)
mesh_3B.upper_right = (x, 60.0, 10.0)
mesh_filter_3B = openmc.MeshFilter(mesh_3B)

tally_3B = openmc.Tally(name="Case 3B")
tally_3B.filters = [mesh_filter_3B]
tally_3B.scores = ['flux']
tally_3B.estimator = estimator

# Case 3C
mesh_3C = openmc.RegularMesh()
mesh_3C.dimension = (x_dim, 1, 1)
mesh_3C.lower_left = (0.0, 90.0, 30.0)
mesh_3C.upper_right = (x, 100.0, 40.0)
mesh_filter_3C = openmc.MeshFilter(mesh_3C)

tally_3C = openmc.Tally(name="Case 3C")
tally_3C.filters = [mesh_filter_3C]
tally_3C.scores = ['flux']
tally_3C.estimator = estimator

# Source
source_filter = openmc.UniverseFilter(su)
tally_source = openmc.Tally(name="Source")
tally_source.filters = [source_filter]
tally_source.scores = ['flux']
tally_source.estimator = estimator

# Void
void_filter = openmc.UniverseFilter(vu)
tally_void = openmc.Tally(name="Void")
tally_void.filters = [void_filter]
tally_void.scores = ['flux']
tally_void.estimator = estimator

# Shield
shield_filter = openmc.MaterialFilter(shield_mat)
tally_shield = openmc.Tally(name="Shield")
tally_shield.filters = [shield_filter]
tally_shield.scores = ['flux']
tally_shield.estimator = estimator

# Far Cell
mesh_far = openmc.RegularMesh()
mesh_far.dimension = (1, 1, 1)
mesh_far.lower_left = (50.0, 90.0, 50.0)
mesh_far.upper_right = (60, 100.0, 60.0)
mesh_filter_far = openmc.MeshFilter(mesh_far)

tally_far = openmc.Tally(name="Case far")
tally_far.filters = [mesh_filter_far]
tally_far.scores = ['flux']
tally_far.estimator = estimator

# Instantiate a Tallies collection and export to XML
tallies = openmc.Tallies([tally_3A, tally_3B, tally_3C, tally_source, tally_void, tally_shield, tally_far])

model = openmc.Model(geometry=geometry, materials=mats, settings=settings, tallies=tallies)

model.convert_to_multigroup(
    method='material_wise', energy_groups='CASMO-2', nparticles=1000,
    overwrite_mgxs_library=True, kinetic=True, num_delayed_groups=6
)

model.settings.timestep_parameters['n_timesteps'] = 5
density_timeseries = np.linspace(1, 0.95, 100)
model.materials[0].set_density(
    'macro', density=1.0, density_timeseries=density_timeseries)

# Convert to a random ray model
model.convert_to_random_ray()

# Overlay mesh of 1cm cubes
mesh = openmc.RegularMesh()
pitch = [1.0, 1.0, 1.0]
mesh.dimension = (60, 100, 60)
mesh.lower_left = (0.0, 0.0, 0.0)
mesh.upper_right = (60.0, 100.0, 60.0)
model.settings.random_ray['source_region_meshes'] = [
    (mesh, [model.geometry.root_universe])]
model.settings.random_ray['time_derivative_method'] = 'isotropic'
model.settings.timestep_parameters['n_timesteps'] = '100'

## Random Ray Settigngs
lower_left = (0.0, 0.0, 0.0)
upper_right = (x, y, z)
uniform_dist = openmc.stats.Box(lower_left, upper_right, only_fissionable=False)
rr_source = openmc.IndependentSource(space=uniform_dist)

model.settings.batches = 1100
model.settings.inactive = 100
#model.settings.particles = 1000
#model.settings.particles = 2810
model.settings.particles = 7500
#model.settings.particles = 10000
model.settings.run_mode = 'fixed source'
model.settings.random_ray['distance_active'] = 400.0
model.settings.random_ray['distance_inactive'] = 150.0
model.settings.random_ray['ray_source'] = rr_source
model.settings.random_ray['volume_normalized_flux_tallies'] = False

model.export_to_model_xml()

