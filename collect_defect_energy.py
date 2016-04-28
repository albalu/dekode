#!/usr/bin/env python
# This code extracts the necessary information from current VASP output folders (self, dielectric, phonon, nself_aMoBT etc)
# and run aMoBT to calculate the electronic properties: mobility, conductivity and thermopower at different temperatures
# Please contact alireza@wustl.edu if you had any questions. Bug reports are very much appreciated.
# By: Alireza Faghaninia and Mike Sullivan

from __future__ import division
import os
import numpy as np
import re
import argparse
import pymatgen as mg


def generate_MATLAB_defect_plot_input(total_defects,defect_types,n_defects):
	with file('defects_dopants_info_cation_rich.m', 'w') as indata:
		indata.write('% This is an input file for defects and neutral dopants information \n')
		indata.write('% Follow this format  \n')
		indata.write('% *at first line enter the # of defects +# of dopants+ # of defect types \n')
		indata.write('% *next line: number of each type of defect/dopant in order \n')
		indata.write('% *next line: The name of the defect (arbitrary) \n')
		indata.write('% *next line: Relative_Fermi space Corrected formation energy (2 numbers) \n')
		indata.write('% this together with the next line info (which must be different that this \n')
		indata.write('% is used to make the linear defect \n')
		indata.write('% formation energy with respect to the Fermi level inside the band gap \n')
		indata.write('% *next line: Relative_Fermi space Corrected formation energy (2 numbers) \n')
		indata.write('% *next line: Charge of this defect \n')
		indata.write('% *next line: empty \n')
		indata.write('% follow this format until defects are done, now for dopants follow this: \n')
		indata.write('% *first line: The name of the dopant (arbitrary) \n')
		indata.write('% *next line: Corrected formation energy \n')
		indata.write('% *next line: type of this defect: n or p \n')
		indata.write('% *next line: empty \n')
		indata.write('% Follow this format until dopants are done too! \n \n')
		indata.write('%3d %3d %3d \n' % (total_defects,0,defect_types))
		indata.write('%3d %3d %3d \n' % (n_defects[0], n_defects[1], n_defects[2]))
	return

def jobs_done():
	x = False
	if os.path.isfile("OUTCAR"):
		with open("OUTCAR") as fp:
			for lin in fp:
				line = lin.split()
				if len(line)>1:
					if line[0]=='Voluntary':
						x = True
	return

def get_TOTEN():
	E = 0.0
	os.system("""grep "TOTEN" OUTCAR > temp.txt""")
	os.system("tail -4 temp.txt | head -1 > temp1.txt")
	with open('temp1.txt','r') as temp:
		li = temp.readline()
		line = li.split()
		if len(line) > 4:
			E = float(line[4])
	os.system('rm temp.txt temp1.txt')
	return E	

def get_E_correction(static_dielectric):
	Ec = 0.0
	os.system("""grep "energy correction for charged system" OUTCAR > temp2.txt""")
	with open('temp2.txt','r') as temp:
		li = temp.readline()
		line = li.split()
		if len(line) > 5:
			Ec = float(line[5])/static_dielectric
	os.system('rm temp2.txt')
	return Ec

def find_defect_and_type(defects,formula):
	formula += 'x'
	elements = []
	types = []
	coeffs = []
	E_elements = []
	for defect in defects:
		defect += 'x'
		if 'V' in defect[0]:
			types.append('v')
			element = defect[2:-1]
		elif '_i' in defect:
			types.append('i')
			element = defect[0:1]
			if '_' in element:
				element = defect[0]
		else:
			types.append('d')
			element = defect[0:1]
			if '_' in element:
				element = defect[0]
		elements.append(element)
		coeffs.append(coefficientof(element,formula))		
		E_elements.append(matproj.get_data(element, prop="energy_per_atom")[0]["energy_per_atom"])
	return elements, types, coeffs, E_elements

def coefficientof(element1,formula):
        n = 1
        if formula[formula.find(element1) + len(element1)] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                if formula[formula.find(element1) + 1 + len(element1)] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                        n = int(formula[formula.find(element1) + len(element1)] + formula[formula.find(element1) + 1 + len(element1)]) 
                else:
                        n = int(formula[formula.find(element1) + len(element1)])
        return n

def find_chempot(element1, energy1, dopant): # This function finds all the compounds composed of element1 and dopant so that the chemical potential of the dopant can be determined
        data = matproj.query(criteria={"elements": {"$all": [element1, dopant]},"nelements": 2},properties=["icsd_id", "pretty_formula", "spacegroup.symbol","nelements","energy_per_atom"])
        formation_energies = np.zeros(len(data))
        for n in range(min([25, len(data)])):
                formula = data[n]["pretty_formula"] + "x"  # just adding a character to avoid error in "coefficientof" function
                print( data[n]["pretty_formula"])
                n_e = coefficientof(element1,formula)
                n_d = coefficientof(dopant,formula)
                formation_energies[n] = (data[n]['energy_per_atom']*(n_e+n_d) - n_e * energy1 - n_d * energy_dopant)/n_d
        formation_energies = np.append(formation_energies,0)
        chem = np.min(np.append(formation_energies,[0]))
        return(chem)

if __name__ == "__main__":

	apikey = 'fDJKEZpxSyvsXdCt'
	from pymatgen.matproj.rest import MPRester
	matproj = MPRester(apikey)

	### Check the input arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-de","--defect_names", help="The list of the name of defects (e.g. ['V_O', 'V_Zn'])", required = False)
	parser.add_argument("-di","--dielectric_constant", help="The dielectric constant of the base material for 1st order Makov-Payne correction", required = False)
	args = parser.parse_args()

############	INPUTS:
	args.defect_names = ['V_O', 'V_Sn', 'V_K']
	args.dielectric_constant = 4.86
	job = 'geom'
	ndefects = 0
	formula = 'K2Sn2O3'
	coeffs = []
	formula_units = 16 # The number of formula units that are in the POSCAR of "undoped" supercell
	VBM_max = 2.309599

############	END OF INPUTS

	elements, types, coeffs, E_elements = find_defect_and_type(args.defect_names,formula)
	os.chdir('undoped' + '/' + job)
	if jobs_done:
		E_undoped = get_TOTEN()
		print(E_undoped)
	os.chdir('../..')
	undoped_formation = E_undoped/formula_units
#	coeffs_sum = sum(int(i) for i in coeffs)
	chemical_potentials = []
	undoped_formation -= sum(float(coeffs[i])*float(E_elements[i]) for i in range(0,len(elements)))
	for i in range(0,len(elements)):
		if elements[i] is 'O':
			chemical_potentials.append(0.0)
		if elements[i] is not 'O':
			chemical_potentials.append(undoped_formation/(2 * int(coeffs[i])))
#	chemical_potentials = [0.0, 0.0, 0.0]
	n_defects = []
	with open('temp_energy.txt','w') as efile:
		counter = 0
		for defect in args.defect_names:
			d_count = 0
			for charge in ['-4', '-3', '-2', '-1', '', '+1', '+2', '+3', '+4'] :
				if os.path.exists(defect + charge):
					d_count += 1
					os.chdir(defect + charge + '/' + job)
					if jobs_done:
						E = get_TOTEN()
						ndefects += 1
						print(E)
						Ec = get_E_correction(args.dielectric_constant)
						print(Ec)
						efile.write(defect + charge + ' \n')
						formation_energy = E+Ec-E_undoped
						if types[counter] is 'v':
							formation_energy += (float(E_elements[counter]) + float(chemical_potentials[counter]))
						elif types[counter] is 'i':
							formation_energy -= (float(E_elements[counter]) + float(chemical_potentials[counter]))
						else:
							print('The doping is not programmed yet! Only the vacancy and interstitials for now')
						if charge is not '':
							formation_energy += int(charge)*VBM_max
						efile.write('%4.2f %8.4f \n' % (0,formation_energy))
						if charge is not '':
							efile.write(charge + ' \n\n')
						else:
							efile.write('0.0 \n\n')
					os.chdir('../..')
			n_defects.append(d_count)
			counter += 1
	print(ndefects)
	print(elements)
	print(types)
	print(coeffs)
	print(E_elements)
	print(undoped_formation)
	print(chemical_potentials)

	generate_MATLAB_defect_plot_input(ndefects,len(args.defect_names),n_defects)
	os.system('cat temp_energy.txt >> defects_dopants_info_cation_rich.m')
	os.system('rm temp_energy.txt')

