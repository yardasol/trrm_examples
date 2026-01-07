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
void_cell = openmc.Cell(fill=None, name='infinite void region')
sheld_cell = openmc.Cell(fill=shield_mat, name='infinite shield region')

box = openmc.M
