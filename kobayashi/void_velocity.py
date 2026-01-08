import openmc
import numpy as np

## Materials
shield_mat = openmc.Material(name="shield")
shield_mat.add_elements_from_formula('B4C')
shield_mat.set_density('g/cc', 2.50)

materials =  openmc.Materials([shield_mat])

## Geometry
void_sphere = openmc.Sphere(r=10)
outer_bound = openmc.Sphere(r=15, boundary_type='vacuum')

void_cell = openmc.Cell(fill=None, region=-void_sphere, name='void region')
shield_cell = openmc.Cell(fill=shield_mat, region=(+void_sphere &
                                                   -outer_bound), name='shield region')

geometry = openmc.Geometry(root=[void_cell, shield_cell])

## Settings
settings = openmc.Settings()
strengths = [1.0] # Good - fast group appears largest (besides most thermal)
midpoints = [100.0]
energy_distribution = openmc.stats.Discrete(x=midpoints,p=strengths)
#energy_distribution = openmc.stats.Uniform(a=90.0, b=100.0)
spatial_distribution = openmc.stats.Point()

source = openmc.IndependentSource(space=spatial_distribution, energy=energy_distribution,  strength=1.0) # works
settings.source = [source]

settings.batches = 100
settings.particles = 1000
settings.run_mode = 'fixed source'

## Tallies
tallies = openmc.Tallies()
ebins = [1e-5, 20.0e6]
groups = openmc.mgxs.EnergyGroups(group_edges=ebins)
inv_vbar = openmc.mgxs.TotalXS(domain=shield_cell, domain_type='cell',
                                       energy_groups=groups)
inv_vbar.by_nuclide = False
for tally in inv_vbar.tallies.values():
    tallies.append(tally)

######a####
## MODEL ##

model = openmc.model.Model(materials=materials, geometry=geometry, settings=settings,
                           tallies=tallies)
sp_path = model.run()
sp = openmc.StatePoint(sp_path)
inv_vbar.load_from_statepoint(sp)
print(inv_vbar.xs_tally.mean.flatten()[0])
print(inv_vbar.xs_tally.std_dev.flatten()[0])
