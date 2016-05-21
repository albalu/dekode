#!/usr/bin/env python
# This code extracts the necessary information from current VASP output folders (self, dielectric, phonon, nself_aMoBT etc)
# and run aMoBT to calculate the electronic properties: mobility, conductivity and thermopower at different temperatures
# Please contact alireza@wustl.edu if you had any questions. Bug reports are very much appreciated.
# By: Alireza Faghaninia and Mike Sullivan

import os

# After high, the arguments are optional (see the function code for more details)
def generate_aMoBT_input(type, T_array, n_array, Bgap, LO, static, high, free_e = 'false', E_deformation_n = 0.0, E_deformation_p = 0.0, kcbm = '0', kvbm = '0'): 
	with file('INPUTS.m', 'w') as indata:
		indata.write('function [T_array, n_array, Bgap, N_dis, k_min0, k_max, k_trans0, k_step_fine0, k_step0, maximum_iterations_for_g_PO, ...\n')
		indata.write('E, dTdz, m, omega_LO, epsilon_s, epsilon_inf, E_deformation_n, E_deformation_p, P_piezo, C_long, C_trans, ...\n')
		indata.write('c_lattice, curve_fit_iteration, folder_of_plots, spin_orbit_coupling, LORBIT, iterate_over_N_dis, free_e, type, ...\n')
		indata.write('kcbm, kvbm, T_trans, bands_n, bands_p, charge, VBM_band_number_override] = INPUTS \n')

		indata.write('[Bgap, default_T, N_dis, k_min0, k_max, k_trans0, k_step_fine0, k_step0, maximum_iterations_for_g_PO, ...\n')
		indata.write('E, dTdz, m, P_piezo, C_long, C_trans, c_lattice, curve_fit_iteration, folder_of_plots, bands_n, bands_p, ...\n')
		indata.write('spin_orbit_coupling, LORBIT, iterate_over_N_dis, free_e, kcbm, kvbm, T_trans, charge, VBM_band_number_override] = ...\n')
		indata.write('initialize;\n')

		indata.write('%s %s; \n' % ('T_array =', T_array))
		indata.write('%s %s; \n' % ('n_array =', n_array))
		indata.write("""free_e = '%s'; \n""" % free_e)
		indata.write("""type = '%s'; \n""" % type)

		indata.write('omega_LO = %f*2*pi*1e12; \n' % LO)
		indata.write('%s %f; \n' % ('epsilon_s =', static))
		indata.write('%s %f; \n' % ('epsilon_inf =', high))
		indata.write('%s %f; \n' % ('E_deformation_n =', E_deformation_n))
		indata.write('%s %f; \n' % ('E_deformation_p =', E_deformation_p))

		if kcbm is not '0':
			indata.write('%s [%s]; \n' % ('kcbm =', kcbm))
		if kvbm is not '0':
			indata.write('%s [%s]; \n' % ('kvbm =', kvbm))

		
		indata.write('%s %f; \n' % ('Bgap =', Bgap))
		if Bgap < 1:
			indata.write('%s %f; \n' % ('Bgap =', 1))
		
	return

def find_reference(scripts_path):
	os.system("cp " + scripts_path + "find_eval_eband.m .")
	os.system("octave -q --eval find_eval_eband.m")
	count = 0
	with open('val_kpoint.mat', "rU") as f:
		for line in f:
			count += 1
			if count == 6:
				kpoint = line
				kpoint = kpoint.split()
				val_kpoint = " ".join(kpoint)
	count = 0
	with open('con_kpoint.mat', "rU") as f:
		for line in f:
			count += 1
			if count == 6:
				kpoint = line
				kpoint = kpoint.split()
				con_kpoint = " ".join(kpoint)
	count = 0
	with open('econ.mat', "rU") as f:
		for line in f:
			count += 1
			if count == 4:
				econ = float(line)
	count = 0
	with open('eval.mat', "rU") as f:
		for line in f:
			count += 1
			if count == 4:
				eval = float(line)
	count = 0
	with open('core.mat', "rU") as f:
		for line in f:
			count += 1
			if count == 4:
				core = float(line)
	os.system("rm *.mat")
	return val_kpoint, con_kpoint, eval, econ, core


def get_me_dielectrics(filename, LO_phonon, TO_phonon):
	count = 0
	with open(filename, "rU") as f:
		for line in f:
       	                count = count + 1
       	                lin = line.split()
       	                if len(lin) > 2:
       	                        if lin[0] == "MACROSCOPIC" and lin[4] == "(including":
       	                                count = -5
       	                if count == -3:
       	                        x = float(lin[0])
       	                elif count == -2:
       	                        y = float(lin[1])
       	                elif count == -1:
       	                        z = float(lin[2])
       	                        count = 0
	static_dielectric = (x + y + z)/3
	highf_dielectric = static_dielectric * (TO_phonon/LO_phonon)**2
	return static_dielectric, highf_dielectric

def prepare_files_and_submit(aMoBT_path, T_array, n_array, Bgap, LO_phonon, static, highf, free_e, E_deformation_n, E_deformation_p, kcbm, kvbm):

	n_type_folder = '1_n-type_aMoBT_free-e=' + free_e
	p_type_folder = '2_p-type_aMoBT_free-e=' + free_e
	os.system('mkdir ' + n_type_folder)
	os.chdir(n_type_folder)
	os.system('rm *')
	os.system('cp ' + aMoBT_path + '* .')
	os.system('rm e_matlab* log.out')
	os.system('cp ../nself_aMoBT/EIGENVAL .')
	if os.path.exists('../p_nself_aMoBT'):
		os.system('cp ../p_nself_aMoBT/EIGENVAL EIGENVAL_p')
	os.system('cp ../nself_aMoBT/PROCAR .')
	os.system('cp ../self/OUTCAR .')
	os.system('cp ../self/DOSCAR .')
	
	generate_aMoBT_input('n', T_array, n_array, Bgap, LO_phonon, static, highf, free_e, E_deformation_n, E_deformation_p, kcbm, kvbm)
	os.system('qsub run.sh')
	os.chdir('../')

	# For p-type
	os.system('rm -r ' + p_type_folder)
	os.system('cp -r ' + n_type_folder + ' ' +  p_type_folder)
	os.chdir(p_type_folder)
	
	generate_aMoBT_input('p', T_array, n_array, Bgap, LO_phonon, static, highf, free_e, E_deformation_n, E_deformation_p, kcbm, kvbm)
	os.system('qsub run.sh')
	os.chdir('../')


def run_aMoBT_on_dekode_results(scripts_path, aMoBT_path, T_array = '[150 200 250 300 350 400 450 500 550 600 650 700 750 800]', n_array = '[1e17 1e18 1e19 1e20 1e21]', free_e = 'both'):

	os.system("cp " + scripts_path + "find_DOS_peaks.py .")
	from find_DOS_peaks import find_DOS_peaks
	LO_phonon, TO_phonon = find_DOS_peaks('phonon/total_dos.dat')

	os.system("cp " + scripts_path + "calc_def_potential.py .")
	from calc_def_potential import calc_def_potential
	E_deformation_p, E_deformation_n = calc_def_potential('deform/ENERGY_INFO.txt')

	static, highf = get_me_dielectrics('./dielectric/OUTCAR', LO_phonon, TO_phonon)

	os.chdir('nself')
	kvbm, kcbm, eval, econ, core = find_reference(scripts_path)
	os.chdir('../')
	Bgap = econ - eval

	if free_e in ['true', 'both']:
		prepare_files_and_submit(aMoBT_path, T_array, n_array, Bgap, LO_phonon, static, highf, 'true', E_deformation_n, E_deformation_p, kcbm, kvbm)
	if free_e in ['false', 'both']:
		prepare_files_and_submit(aMoBT_path, T_array, n_array, Bgap, LO_phonon, static, highf, 'false', E_deformation_n, E_deformation_p, kcbm, kvbm)
