#!/usr/bin/env python

import os
import argparse
import pymatgen as mp

def make_input(id, potcar_path, amobt_path, scripts_path, GEOM = False, SELF = False, NSELF = False, NSELF_AMOBT = False, DIEL = False, PHONON = False, DEFORM = False, AMOBT = False, SOC = False):
	mp_api_key = 'fDJKEZpxSyvsXdCt'
	with open('MIKECAR','w') as input:
		input.write('EMAIL = alireza@wustl.edu \n')
		input.write('MP_API_KEY = ' + mp_api_key + ' \n')
		input.write('JOB_NAME = See_Folder \n')
		input.write('COMP_NAME = ' + id + ' \n')
		input.write('%s %s \n' % ('GEOM =', GEOM))
		input.write('%s %s \n' % ('SELF =', SELF))
		input.write('%s %s \n' % ('NSELF =', NSELF))
		input.write('%s %s \n' % ('NSELF_AMOBT =', NSELF_AMOBT))
		input.write('%s %s \n' % ('DIEL =', DIEL))
		input.write('%s %s \n' % ('PHONON =', PHONON))
		api = mp.MPRester(mp_api_key)
		structure = api.get_structure_by_material_id(id)
		structure.to(filename="POSCAR")
		with open('POSCAR','r') as poscar:
			counter = 0
			natoms = 0
			for line in poscar:
				counter += 1
				if counter == 7:
					for i in line.split():
						natoms += int(i)
		os.system('rm POSCAR')
		if natoms < 17:
			input.write('DIM = 2x2x2 \n')
		else:
			input.write('DIM = 1x1x1 \n')
		input.write('%s %s \n' % ('DEFORM =', DEFORM))
		input.write('RANGE = -5,5 \n')
		input.write('POSCAR = default \n')
		input.write('INCAR = default \n')
		input.write('%s %s \n' % ('AMOBT =', AMOBT))
		input.write('%s %s \n' % ('SOC =', SOC))	
		input.write('%s %s \n' % ('AMOBT_PATH =', amobt_path)) 
		input.write('%s %s \n' % ('SCRIPTS_PATH =', scripts_path))
		input.write('%s %s \n' % ('POTCAR_PATH =', potcar_path))

def run_dekode_for(materials_list, potcar_path, amobt_path, scripts_path, GEOM = False, SELF = False, NSELF = False, NSELF_AMOBT = False, DIEL = False, PHONON = False, DEFORM = False, AMOBT = False, SOC = False):
	if SOC:
#		if ~os.path.exists('SOC')
		os.system('mkdir SOC')
		os.chdir('SOC')
	for id in materials_list:
## Uncomment #1 if you want to start from the beginning
		os.system('mkdir ' + id) 
		os.system('%s %s%s %s' % ('cp', scripts_path, 'dekode.py', id))
		os.system('%s %s%s %s' % ('cp', scripts_path, 'partita.sh', id))
		os.system('cp ~/vasp-ib2.csh ' + id)
		os.chdir(id)
#		make_input(id, amobt_path, scripts_path, SOC) #1
		make_input(id, potcar_path, amobt_path, scripts_path, GEOM, SELF, NSELF, NSELF_AMOBT, DIEL, PHONON, DEFORM, AMOBT, SOC)
		os.system('rm python_job.*')
		os.system('qsub partita.sh')
		os.chdir('../')

if __name__ == "__main__":
	
	# The following are the first 9 n-type TCO's
	amobt_path = '/research-projects/partita/faghaniniaa/current_jobs/carrier_scattering/VERSIONS/latest_aMoBT/'
	scripts_path = '~/scripts/dekode_scripts/'
	potcar_path = '/cluster/caml/vasp-pot/PBE/'

	list1 = ['mp-5966', 'mp-22598', 'mp-19803', 'mp-29213', 'mp-22323', 'mp-22189', 'mp-31132', 'mp-8275', 'mp-13334', 'mp-3443', 'mp-3810', 'mp-16281']
	list2 = ['mp-3188', 'mp-1243', 'mp-504908', 'mp-29297', 'mp-566788', 'mp-10913', 'mp-28931', 'mp-13803', 'mp-5794', 'mp-8285', 'mp-3917', 'mp-19148']
	list3 = ['mp-1705', 'mp-30284', 'mp-886', 'mp-25178', 'mp-27175', 'mp-540728', 'mp-5280', 'mp-19006', 'mp-3056', 'mp-7534']
	list4 = ['mp-8922', 'mp-7762', 'mp-13820', 'mp-20546', 'mp-27843', 'mp-540688', 'mp-27563', 'mp-8086', 'mp-25014', 'mp-19321']
	list5 = ['mp-7831', 'mp-16293', 'mp-3653', 'mp-29910', 'mp-29455', 'mp-25043', 'mp-10486', 'mp-5909', 'mp-22937', 'mp-29606', 'mp-2951'] 
	list6 = ['mp-4590', 'mp-541368', 'mp-27684', 'mp-22734', 'mp-7461', 'mp-20337', 'mp-23419']
	list7 = ['mp-5380', 'mp-7863', 'mp-8624', 'mp-3744', 'mp-7502', 'mp-1346', 'mp-20694', 'mp-761872']
	sarmandi = ['mp-7233', 'mp-4764']    # X2SeO2, X= La, Pr, Nd, Gd
	zero_gaps = ['mp-13971', 'mp-2045']    # X2SeO2, X=  Pr, Nd, Gd mp-19079 (zero-gap even on MP)
	pTCO_SI_list1 = ['mp-28962', 'mp-13060', 'mp-617']
	pTCO_SI_list2 = ['mp-5709', 'mp-18288', 'mp-28711', 'mp-23487'] 
	pTCO_SI_list3 = ['mp-25726', 'mp-3370', 'mp-4086', 'mp-2931', 'mp-17559', 'mp-8111']
	TE1 = ['mp-22619', 'mp-486', 'mp-555818', 'mp-2074', 'mp-7955', 'mp-991676', 'mp-9295', 'mp-991652']  # NiP2, NiP2, SiCu2PbS4, Li3Sb, Li3Sb, (Nb-Ta-V)Cu3Te4

	famous = ['mp-2133', 'mp-3163', 'mp-22598', 'mp-22323', 'mp-644741'] # 			ZnO, BaSnO3, 3_In2O3 
	famous1= ['mp-856', 'mp-550172', 'mp-755071', 'mp-545544', 'mp-23092', 'mp-552200']  #  3_SnO2, 3_Ba2TaBiO6
	missed = ['mp-5966', 'mp-22598', 'mp-19803', 'mp-29213', 'mp-14243', 'mp-22189', 'mp-8275', 'mp-13334', 'mp-3443', 'mp-3810', 'mp-16281','mp-566788','mp-19321','mp-22189']
#	excluded_first_pass = ['mp-510309', 'mp-22606', 'mp-505501']	# NONE OF THESE COULD BE READ FROM MATERIALSPROJECT
#	566788: n cannot be obtained in aMoBT!
	famous_p = ['mp-10695', 'mp-560588', 'mp-3748', 'mp-3098', 'mp-4979']	# ZnS_2, CuAlO2_2, CuAlS2
	famous_p_2 = ['mp-5970', 'mp-4255', 'mp-19281', 'mp-19357', 'mp-18841']	# BaCu2S2_2, SrxLa1-xCrO3_3

# mp-21905, mp-3331 and mp-29047 don't exist on MP website
	so_list = ['mp-8298', 'mp-8299', 'mp-7787', 'mp-19845', 'mp-8789', 'mp-3519']
#	materials_list = list1 + list2 + list3 + list4 + list5 + list6 + list7
	materials_list = list2 + list3 + list4 + list5 + list6 + list7 + sarmandi + pTCO_SI_list1 + pTCO_SI_list2 + pTCO_SI_list3 + so_list + zero_gaps + famous + famous1

#	materials_list = ['mp-569522'] # MnP4
#	materials_list = ['mp-16764']  # RbYTe2
#	materials_list = ['mp-16763']  # KYTe2
#	materials_list = ['mp-945184'] # YCyTe2
#	materials_list = ['mp-12953']  # TmAgTe2
#	materials_list = ['mp-4753']  # Al2SiO5
#	materials_list = ['mp-487', 'mp-14587' ,'mp-570553']  # MnP4, ZnP4, FeP4
#	materials_list = ['mp-7623']  # MgAs4 
#	materials_list = ['mp-7904']  # CdP4 
#	materials_list = ['mp-384']  # MgP4 
#	materials_list = ['mp-19717']  # PbTe
#	materials_list = sarmandi
#	materials_list = ['mp-7541']  # SnP3
#	materials_list = pTCO_SI_list3
#	materials_list = ['mp-640889']  # TmCu3Te3
	occasional_TEs = ['mp-569522', 'mp-16764', 'mp-16763', 'mp-945184', 'mp-12953', 'mp-4753', 'mp-487', 'mp-14587' ,'mp-570553', 'mp-7623', 'mp-7904', 'mp-384', 'mp-19717', 'mp-7541', 'mp-640889']
#	materials_list = occasional_TEs + TE1

	SOC = False


# List of manuals: 

#		'mp-21905'
#		'mp-13973'

	parser = argparse.ArgumentParser()
	parser.add_argument("-pa","--mp_id", help="The Materials Project ID", required = False)
	args = parser.parse_args()

#	run_dekode_for(famous_p_2, potcar_path, amobt_path, scripts_path, GEOM = True, SELF = True, NSELF = True, \
#	NSELF_AMOBT = True, DIEL = True, PHONON = True, DEFORM = True, AMOBT = True, SOC = False)

#	run_dekode_for(['mp-7831', 'mp-541368', 'mp-22734', 'mp-7863', 'mp-3744', 'mp-7502', 'mp-7233', 'mp-5709'], potcar_path, amobt_path, scripts_path, GEOM = False, SELF = False, NSELF = False, \
#	NSELF_AMOBT = False, DIEL = False, PHONON = False, DEFORM = False, AMOBT = True, SOC = False)

#	run_dekode_for(['mp-16281','mp-566788','mp-19321','mp-22189'], potcar_path, amobt_path, scripts_path, GEOM = False, SELF = False, NSELF = False, \
#	NSELF_AMOBT = False, DIEL = False, PHONON = False, DEFORM = False, AMOBT = True, SOC = False)
