#!/usr/bin/env python
# This code will check the folder and some subfolder assigned by the user to see if the mp-*** listed in a text file are available or not
# If available, the selected property at selected concentration and temperature will be reported
# If not, N.A would be typed in front of the list
# By: Alireza Faghaninia


#!/usr/bin/env python

import argparse
import os
scripts_path = '~/dekode/'
os.system('cp ' + scripts_path + 'run_aMoBT.py .')
from run_aMoBT import find_reference, get_me_dielectrics
os.system("cp " + scripts_path + "calc_def_potential.py .")
from calc_def_potential import calc_def_potential
os.system('cp ' + scripts_path + 'find_DOS_peaks.py .')
from find_DOS_peaks import find_DOS_peaks

def find_properties(filename, n, T): #find the transport properties at a given n and T from aMoBT output
	count = 0
	mobility = 0
	conductivity = 0
	thermopower = 0
	at_correct_n = False
	if os.path.exists(filename):
		with open(filename) as aMoBT_output:
			for row in aMoBT_output:
				line = row.split()
				if at_correct_n:
					if float(line[0]) == T:
						mobility = float(line[1])
						conductivity = float(line[2])
						thermopower = float(line[3])
						at_correct_n = False
				if len(line) > 3:
					if 'Carrier' in line[0] and float(line[3]) == n:
						at_correct_n = True
	return mobility, conductivity, thermopower

def find_effective_mass(filename):
	m_e = 0.0000
	m_h = 0.0000
	if os.path.exists(filename):
		with open(filename) as aMoBT_output:
			for row in aMoBT_output:
				line = row.split()
				if len(line) >= 2:
					if line[0] == '***Proceed':
						if 'm*_e/m' in line[7]:
							m_e = float(line[9])
						if 'm*_h/m' in line[7]: 
							m_h = float(line[9])
	return m_e, m_h

def total_time(job_list):	# job_list is a list of string of jobs in the subfolders, i.e. geom, self, phonon, etc
        t_total = 0.0
        for job in job_list:
                if os.path.exists(job):
                        os.chdir(job)
                        if os.path.exists('OUTCAR'):
                                with open('OUTCAR', 'r') as outcar:
                                        for line in outcar:
                                                if 'Elapsed time (sec):' in line:
                                                        l = line.split()
                                                        t_total += float(l[3])
                        if 'deform' in job:
                                for j in ['-10', '-9', '-8', '-7', '-6', '-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
                                        if os.path.exists('part' + j):
                                                os.chdir('part' + j)
                                                if os.path.exists('OUTCAR'):
                                                        with open('OUTCAR', 'r') as outcar:
                                                                for line in outcar:
                                                                        if 'Elapsed time (sec):' in line:
                                                                                l = line.split()
                                                                                t_total += float(l[3])

                                                os.chdir('../')
                        os.chdir('../')
        return(t_total)




if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--filename", help="The filename that contains the list, default=checklist",	required=False, default="checklist")
	parser.add_argument("-n", "--n", help="Carrier concentration", required=False, default=1e20)
	parser.add_argument("-d", "--detail", help="How much detail in data, more or less", required=False, default="less")
	parser.add_argument("-dir", "--dir", help="The folder name under which the AMSET calculations are, default = None", required=False, default=None)
	parser.add_argument("-T", "--T", help="Temperature(K)", required=False, default=300)
	parser.add_argument("-fr", "--free_e", help="To use free-electron density of states or not (true or false)", required=False, default="true")
	parser.add_argument("-fo", "--formula", help="Whether to print formulas or not (options: T or F)", required=False, default=False)
	args = parser.parse_args()
	if args.formula in ['T', 't', 'true', 'True', 'TRUE']:
		args.formula = True
	else:
		print('\nYou can include the formula of each material in status.txt by using --fo t\n')

	print("You can get more data (e.g. dielectric constants) by using -d more option\n")
	folders = ['./', 'new_TEs/', 'new_TCOs/']

	if args.dir:
		n_type_folder = os.path.join(args.dir, '1_n-type_aMoBT_free-e=' + args.free_e)
		p_type_folder = os.path.join(args.dir, '2_p-type_aMoBT_free-e=' + args.free_e)
	else:
		n_type_folder = '1_n-type_aMoBT_free-e=' + args.free_e
		p_type_folder = '2_p-type_aMoBT_free-e=' + args.free_e

	clist = []
	swd = os.getcwd()
	with open(args.filename,'r') as raw_list:
		for line in raw_list:
			if len(line)>1:
				supposed_id = line.split()[0]
				# if ('mp-' in supposed_id) or ('mvc-' in supposed_id):
				clist.append(line.split()[0])
	stat = open('status.txt', 'w')
	rem = open('remaining.txt', 'w')
	stat.write('n={} T={}\n'.format(str(args.n), str(args.T)))
	rem.write('n={} T={}\n'.format(str(args.n), str(args.T)))
	if args.detail == "less":
		stat.write('%30s%12s%12s%12s %10s%7s%10s%10s%10s%7s%9s%9s\n' % ('location_of_mp-id_if-any', 'formula', 'mu-cm2/V.s', 'sigma-S/cm', 'S-uV/K', 'PF', 'p_mu', 'p_sigma', 'p_S', 'p_PF', 'm_e', 'm_h'))
	elif args.detail == "more":
		stat.write('%30s%12s%12s%12s %10s%7s%10s%10s%10s%7s%9s%9s%8s%8s%7s%7s%6s%6s\n' % ('location_of_mp-id_if-any', 'formula', 'mu-cm2/V.s', 'sigma-S/cm', \
			'S-uV/K', 'PF', 'p_mu', 'p_sigma', 'p_S', 'p_PF', 'm_e', 'm_h',\
				'omegaLO', 'omegaTO', 'eps0', 'epsinf', 'nEdef', 'pEdef'))
	for c in clist:
		if ":" in c:
			stat.write(c + "\n")
			continue
		formula = c
		if args.formula:
			try:
				apikey = 'fDJKEZpxSyvsXdCt'
				from pymatgen.matproj.rest import MPRester
				matproj = MPRester(apikey)
				formula = matproj.get_data(c, prop="pretty_formula")[0]["pretty_formula"]
				spacegroup = matproj.get_data(c, prop="spacegroup")[0]["spacegroup"]
			except:
				formula = 'API-failed'
		proceed = False
		for subf in folders:
			if os.path.exists(subf + c):
				proceed = True
				c_path = subf + c
		if proceed:
			os.chdir(c_path)
			
			if args.detail == "more":
				os.chdir('nself')
        	                val_kpoint, con_kpoint, eval, econ, core = find_reference(scripts_path)
                	        os.chdir('../')
				try:
	                        	LO_phonon, TO_phonon = find_DOS_peaks('phonon/total_dos.dat')
        	                	try:
						static_dielectric, highf_dielectric = get_me_dielectrics('./dielectric/OUTCAR', LO_phonon, TO_phonon)
					except:
						static_dielectric = highf_dielectric = 0
				except:
					LO_phonon= TO_phonon = static_dielectric = highf_dielectric = 0
				try:
					E_deformation_p, E_deformation_n = calc_def_potential('deform/ENERGY_INFO.txt')
				except:
					E_deformation_p = E_deformation_n = 0
				#t_tot = total_time(['geom', 'self', 'nself', 'nself_aMoBT', 'p_nself_aMoBT', 'dielectric', 'phonon', 'deform'])
			
			mobility_n, conductivity_n, thermopower_n = find_properties(n_type_folder + '/aMoBT_output.txt', float(args.n), float(args.T))
			mobility_p, conductivity_p, thermopower_p = find_properties(p_type_folder + '/aMoBT_output.txt', float(args.n), float(args.T))
			m_e, m_h_dummy = find_effective_mass(n_type_folder + '/log.out')
			m_e_dummy, m_h = find_effective_mass(p_type_folder + '/log.out')
			

			os.chdir(swd)
			if mobility_n > 10000:
				mobility_n = 10000
			if abs(mobility_p) > 10000:
				mobility_p = 10000
			if abs(thermopower_n) > 10000:
				thermopower_n = 10000
			if abs(thermopower_p) > 10000:
				thermopower_p = 10000
			if abs(mobility_n) >= 10000 or abs(mobility_p) >= 10000 or abs(thermopower_n) >= 10000 or abs(thermopower_p) >= 10000:
				mobility_n = "N/A"
				mobility_p = "N/A"
				thermopower_n = "N/A"
				thermopower_p = "N/A"				
			if args.detail == "less":
				try:
					stat.write('%30s,%12s,%12.2f,%12.2f ,%10.2f,%7.2f,%10.2f,%10.2f,%10.2f,%7.2f,%9.4f,%9.4f\n' % (c_path.split("/")[-1], formula, mobility_n, conductivity_n, thermopower_n, conductivity_n*thermopower_n**2/1e6, mobility_p, conductivity_p, thermopower_p, conductivity_p*thermopower_p**2/1e6, m_e, m_h))
				except:
					stat.write('%30s,%12s,%12s,%12s ,%10s,%7s,%10s,%10s,%10s,%7s,%9.4f,%9.4f\n' % (c_path.split("/")[-1], formula, mobility_n, "N/A", thermopower_n, "N/A", mobility_p,"N/A", thermopower_p, "N/A", m_e, m_h))				
			elif args.detail == "more":
				stat.write('%30s,%12s,%12.2f,%12.2f ,%10.2f,%7.2f,%10.2f,%10.2f,%10.2f,%7.2f,%9.4f,%9.4f,%8.2f,%8.2f,%7.2f,%7.2f,%6.2f,%6.2f\n' %\
				 (c_path, formula, mobility_n, conductivity_n, thermopower_n, conductivity_n*thermopower_n**2/1e6, 
					mobility_p, conductivity_p, thermopower_p, conductivity_p*thermopower_p**2/1e6, m_e, m_h,
						LO_phonon, TO_phonon, static_dielectric, highf_dielectric, E_deformation_n, E_deformation_p))
		else:
			stat.write('%30s,%12s\n' % (c, 'N/A'))
#			mpstart = c.find('mp-')
#			rem.write(c[mpstart:] + '\n')
			rem.write(c + '\n')
		
	stat.close()
	rem.close()
	print('\nDONE! see status.txt and remaining.txt')
	print('Number of entries {0}'.format(len(clist)))
	print('Number of unique IDs {0}'.format(len(set(clist))))
