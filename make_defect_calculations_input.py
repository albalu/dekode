#!/usr/bin/env python
# This code generates the necessary inout files to calculate defect formation energies
# Please contact alireza@wustl.edu if you had any questions. Bug reports are very much appreciated.
# By: Alireza Faghaninia and Mike Sullivan

import os
import numpy as np
import re
import argparse

from tempfile import mkstemp
from shutil import move
from os import remove, close
#import pymatgen as mp

def replace(file,newfile,pattern,subst):
#	Create temp file
	fh, abs_path = mkstemp()
	with open(abs_path,'w') as new_file:
		with open(file) as old_file:
			for line in old_file:
				new_file.write(line.replace(pattern, subst))
	close(fh)
#	Move new file
	move(abs_path, newfile)

if __name__ == "__main__":
	
##########################################	INPUTS:

	charges = ['-4', '-3', '-2', '-1', '+1', '+2']  ### It's important to have the + in the positive charges to facilitate the reading of the results
	natoms = 55 # for now I manually subtract one atom because all defects are vacancy. Make sure to switch undoped back to natoms+1
	defects = ['V_Sr', 'V_As', 'V_O']
	defects_e_change = [-10, -5, -6] # This means by introducing the defect, how many electrons are removed (e.g. -6 for one oxygen vacancy, V_O
	defect_coordinate = ['0.5 0.75 0.5', '0.56803 0.56803 0.636059', '0.25 0.75 0.5']
	NELECT_undoped = 448

#########################################	END OF INPUTS

### Making/finishing the undoped system
	os.chdir('undoped')
	if not os.path.exists('geom'):
		os.system('mkdir geom')
	if not os.path.exists('dos'):
		os.system('mkdir dos')
	if not os.path.exists('HSE_dos'):
		os.system('mkdir HSE_dos')
	os.chdir('geom')
	with open ('INCAR','w') as incar:
		incar.write('ALGO = Fast \n')
		incar.write('EDIFF = 0.0011 \n')
		incar.write('ENCUT = 520 \n')
		incar.write('IBRION = 2 \n')
		incar.write('ICHARG = 1 \n')
		incar.write('ISIF = 3 \n')
		incar.write('ISMEAR = -5 \n')
		incar.write('ISPIN = 2 \n')
		incar.write('LORBIT = 11 \n')
		incar.write('LREAL = Auto \n')
		incar.write('LWAVE = False \n')
		incar.write('MAGMOM = ' + str(natoms) + '*0.6 \n')
		incar.write('NELM = 100 \n')
		incar.write('NSW = 99 \n')
		incar.write('PREC = Accurate \n')
		incar.write('SIGMA = 0.05 \n')

	os.system('cp INCAR ../dos/.')
	os.chdir('../dos/')
	replace('INCAR', 'INCAR','ALGO = Fast', 'ALGO = Normal')
	replace('INCAR', 'INCAR','EDIFF = 0.0011', 'EDIFF = 2.2e-05')
	replace('INCAR', 'INCAR','NSW = 99', 'NSW = 0')
	replace('INCAR', 'INCAR','IBRION = 2', 'IBRION = -1')
	replace('INCAR', 'INCAR','LWAVE = False', 'LWAVE = True')
	replace('INCAR', 'INCAR','ICHARG = 1', 'ICHARG = 0')
	with open('incar_addition','w') as incar:
		incar.write('NEDOS = 3001 \n')
		incar.write('LCHARGE = True \n')
		incar.write('LAECHG = True \n')
		incar.write('LCHARG = True \n')
		incar.write('LVHAR = True \n')
	os.system('cat incar_addition >> INCAR')
	os.chdir('../')
	if os.path.exists('HSE_dos'):
		os.system('cp dos/* HSE_dos/.')
	else:
		os.system('cp -r dos HSE_dos/')
	os.chdir('HSE_dos')
	replace('INCAR', 'INCAR','ALGO = Normal','ALGO = Damped')
	with open('incar_addition','w') as incar:
		incar.write('HFSCREEN = 0.2 \n')
		incar.write('PRECFOCK = Normal \n')
		incar.write('    TIME = 0.4 \n')
		incar.write('LMAXFOCK = 4 \n')
		incar.write('  NKREDX = 1 \n')
		incar.write('  NKREDY = 1 \n')
		incar.write('  NKREDZ = 1 \n')
		incar.write(' LHFCALC = .TRUE. \n')
	os.system('cat incar_addition >> INCAR')
	os.chdir('../..')
	
	counter = 0
	for defect in defects:
		os.system('mkdir ' + defect)
		os.chdir(defect)
		os.system('mkdir geom')
		os.system('cp ../undoped/geom/POTCAR geom/.')
		os.system('cp ../POSCAR' + defect + ' geom/POSCAR')
		os.system('cp ../undoped/geom/KPOINTS geom/.')
		os.system('cp ../undoped/geom/INCAR geom/.')
		os.system('mkdir dos')
		os.system('cp ../undoped/dos/INCAR dos/.')
		os.chdir('dos')
		with open('incar_addition','w') as incar:
			incar.write('IDIPOL = 4 \n')
			incar.write('DIPOL = ' + defect_coordinate[counter] + ' \n')
		os.system('cat incar_addition >> INCAR')
		os.chdir('../')

		os.system('mkdir HSE_dos')
		os.system('cp ../undoped/HSE_dos/INCAR HSE_dos/.')
		os.system('cat dos/incar_addition >> HSE_dos/INCAR')

		os.chdir('../')

		for charge in charges:
			if not os.path.exists(defect + charge):
				os.system('cp -r ' + defect + ' ' + defect + charge)
				os.chdir(defect + charge)
				os.chdir('geom')
				with open('incar_addition','w') as incar:
					incar.write('NELECT = ' + str(NELECT_undoped + defects_e_change[counter] - int(charge)) + ' \n')
				os.system('cat incar_addition >> INCAR')
				os.chdir('../')
				os.system('cat geom/incar_addition >> dos/INCAR')
				os.system('cat geom/incar_addition >> HSE_dos/INCAR')
				os.chdir('../')
		counter += 1

