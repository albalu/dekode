#!/usr/bin/env python
# This code will collect and summarize all the information for each material that have been run
# Please contact alireza@wustl.edu if you had any questions. Bug reports are very much appreciated.
# By: Alireza Faghaninia

list1 = ['mp-5966', 'mp-22598', 'mp-19803', 'mp-29213', 'mp-22323', 'mp-22189', 'mp-31132', 'mp-8275', 'mp-13334', 'mp-3443', 'mp-3810', 'mp-16281']
list2 = ['mp-3188', 'mp-1243', 'mp-504908', 'mp-29297', 'mp-10913', 'mp-28931', 'mp-13803', 'mp-5794', 'mp-8285', 'mp-3917']
list3 = ['mp-1705', 'mp-30284', 'mp-886', 'mp-25178', 'mp-27175', 'mp-540728', 'mp-5280', 'mp-3056', 'mp-7534']
list4 = ['mp-8922', 'mp-7762', 'mp-13820', 'mp-20546', 'mp-27843', 'mp-540688', 'mp-27563', 'mp-8086', 'mp-25014']
list5 = ['mp-7831', 'mp-16293', 'mp-3653', 'mp-29910', 'mp-29455', 'mp-10486', 'mp-5909', 'mp-22937', 'mp-29606', 'mp-2951'] 
list6 = ['mp-4590', 'mp-541368', 'mp-27684', 'mp-22734', 'mp-7461', 'mp-20337', 'mp-23419']
list7 = ['mp-5380', 'mp-7863', 'mp-8624', 'mp-3744', 'mp-7502', 'mp-1346', 'mp-20694', 'mp-761872']
sarmandi = ['mp-7233', 'mp-4764']    # X2SeO2, X= La, Pr, Nd, Gd
zero_gaps = ['mp-13971']    # X2SeO2, X=  Pr, Nd, Gd
pTCO_SI_list1 = ['mp-28962', 'mp-13060', 'mp-617']
pTCO_SI_list2 = ['mp-5709', 'mp-18288', 'mp-28711', 'mp-23487'] 
pTCO_SI_list3 = ['mp-25726', 'mp-3370', 'mp-4086', 'mp-2931', 'mp-17559', 'mp-8111']
TE1 = ['mp-22619', 'mp-486', 'mp-555818', 'mp-2074', 'mp-7955', 'mp-991676', 'mp-9295', 'mp-991652']  # NiP2, NiP2, SiCu2PbS4, Li3Sb, Li3Sb, (Nb-Ta-V)Cu3Te4

famous = ['mp-2133', 'mp-3163', 'mp-22323', 'mp-644741'] # 			ZnO, BaSnO3, 3_In2O3 
famous1= ['mp-856', 'mp-550172', 'mp-755071', 'mp-545544', 'mp-23092', 'mp-552200']  #  3_SnO2, 3_Ba2TaBiO6
missed = ['mp-5966', 'mp-22598', 'mp-19803', 'mp-29213', 'mp-14243', 'mp-22189', 'mp-8275', 'mp-13334', \
	  'mp-3443', 'mp-3810', 'mp-16281', 'mp-566788','mp-19321','mp-22189']

famous_p = ['mp-10695', 'mp-560588', 'mp-3748', 'mp-3098', 'mp-4979']	# ZnS_2, CuAlO2_2, CuAlS2
famous_p_2 = ['mp-5970', 'mp-4255', 'mp-19281', 'mp-19357', 'mp-18841']	# BaCu2S2_2, SrxLa1-xCrO3_3

excluded_first_pass = ['mp-510309', 'mp-22606', 'mp-505501']  # the POSCARs couldn't be found through pymatgen

# mp-21905, mp-3331 and mp-29047 don't exist on MP website
so_list = ['mp-8298', 'mp-8299', 'mp-7787', 'mp-19845', 'mp-8789', 'mp-3519']
#	materials_list = list1 + list2 + list3 + list4 + list5 + list6 + list7
materials_list = list2 + list3 + list4 + list5 + list6 + list7 + sarmandi + pTCO_SI_list1 + pTCO_SI_list2 + pTCO_SI_list3 + so_list + zero_gaps + famous + famous1 +  missed + famous_p
exceptions = ['mp-755071', 'mp-566788', 'mp-19321', 'mp-29910', 'mp-5709', 'mp-29213', 'mp-14243', 'mp-3098']

#exceptions = ['mp-755071', 'mp-29297','mp-1705','mp-30284','mp-540728','mp-8922','mp-7762','mp-29910','mp-541368','mp-2951','mp-22734','mp-23419',\
#'mp-23419','mp-7863','mp-7502','mp-7233' ,'mp-28962','mp-5709'   ,'mp-23487','mp-2931'   ,'mp-17559','mp-8298','mp-8299','mp-7787','mp-19845','mp-8789','mp-3519']

n = 1e20
stn = '%5.2e' % n
T = 300
free_e = 'true'
n_type_folder = '1_n-type_aMoBT_free-e=' + free_e
p_type_folder = '2_p-type_aMoBT_free-e=' + free_e

for r in exceptions:
	if r in materials_list:
		materials_list.remove(r)

# errors: mp-19321
# zero gaps: 566788 19148 19006
# zero gaps: 19079 25043 2045  (mp-19079 (zero-gap even on MP))
# Check later: 22598 (In2O3 belongs to famous)

scripts_path = '~/scripts/dekode_scripts/'

import os
os.system('cp ' + scripts_path + 'run_aMoBT.py .')
from run_aMoBT import find_reference
os.system('cp ' + scripts_path + 'find_DOS_peaks.py .')
from find_DOS_peaks import find_DOS_peaks

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



#materials_list = ['mp-16764']
print(materials_list)

apikey = 'fDJKEZpxSyvsXdCt'
from pymatgen.matproj.rest import MPRester
matproj = MPRester(apikey)
with open('DATA_ALL.txt', 'w') as data:
#	data.write('%12s %12s %9s %22s %22s %7s %7s %7s %8s %8s %8s %8s %16s %16s %11s \n' % ('MP-ID', 'Formula', 'gap(eV)', 'n-cond_' + stn + '_' + str(T) + 'K', 'p-cond_' + stn + '_' + str(T) + 'K', 'LO-phon', 'eps_0', 'eps_inf', 'm_e', 'm_h', 'mu_n', 'mu_p', 'time(s)'))
	data.write('%12s %12s %9s %22s %22s %7s %7s %7s %8s %8s %8s %8s %11s \n' % ('MP-ID', 'Formula', 'gap(eV)', 'n-cond_' + stn + '_' + str(T) + 'K', 'p-cond_' + stn + '_' + str(T) + 'K', \
	'LO-phon', 'eps_0', 'eps_inf', 'm_e', 'm_h', 'mu_n', 'mu_p', 'time(s)'))
	for id in materials_list:
		formula = matproj.get_data(id, prop="pretty_formula")[0]["pretty_formula"]
		if os.path.exists(id):
			print(id)
			os.chdir(id)
			os.chdir('nself')
			val_kpoint, con_kpoint, eval, econ, core = find_reference(scripts_path)
			os.chdir('../')
		        LO_phonon, TO_phonon = find_DOS_peaks('phonon/total_dos.dat')
	
			static_dielectric, highf_dielectric = get_me_dielectrics('./dielectric/OUTCAR', LO_phonon, TO_phonon)

			mobility_n, conductivity_n, thermopower_n = find_properties(n_type_folder + '/aMoBT_output.txt', n, T)
			mobility_p, conductivity_p, thermopower_p = find_properties(p_type_folder + '/aMoBT_output.txt', n, T)
			m_n, m_h = find_effective_mass(n_type_folder + '/log.out')
			t_tot = total_time(['geom', 'self', 'nself', 'nself_aMoBT', 'p_nself_aMoBT', 'dielectric', 'phonon', 'deform'])

			os.chdir('../')
#			data.write('%12s %12s %9.2f %22.2f %22.2f %7.2f %7.2f %7.2f %8.4f %8.4f %8.2f %8.2f %16.2f %16.2f %11.2f \n' % (id, formula, econ - eval, conductivity_n, conductivity_p, LO_phonon,  static_dielectric, highf_dielectric, m_n, m_h, mobility_n, mobility_p, thermopower_n, thermopower_p, t_tot))
			data.write('%12s %12s %9.2f %22.2f %22.2f %7.2f %7.2f %7.2f %8.4f %8.4f %8.2f %8.2f %11.2f \n' % \
			(id, formula, econ - eval, conductivity_n, conductivity_p, LO_phonon,  static_dielectric, \
			highf_dielectric, m_n, m_h, mobility_n, mobility_p, t_tot))
