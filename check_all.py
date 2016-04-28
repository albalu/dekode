#!/usr/bin/env python
# This code will check all of the jobs for each material that have been run
# via "dekode.py" and write the address of incomplete job in "incomplete_jobs.txt"
# Please contact alireza@wustl.edu if you had any questions. Bug reports are very much appreciated.
# By: Alireza Faghaninia


# The following are the first 9 n-type TCO's

list1 = ['mp-5966', 'mp-22598', 'mp-19803', 'mp-29213', 'mp-22323', 'mp-22189', 'mp-31132', 'mp-8275', 'mp-13334', 'mp-3443', 'mp-3810', 'mp-16281']
list2 = ['mp-3188', 'mp-1243', 'mp-504908', 'mp-29297', 'mp-566788', 'mp-10913', 'mp-28931', 'mp-13803', 'mp-5794', 'mp-8285', 'mp-3917', 'mp-19148']
list3 = ['mp-1705', 'mp-30284', 'mp-886', 'mp-25178', 'mp-27175', 'mp-540728', 'mp-5280', 'mp-19006', 'mp-3056', 'mp-7534']
list4 = ['mp-8922', 'mp-7762', 'mp-13820', 'mp-20546', 'mp-27843', 'mp-540688', 'mp-27563', 'mp-8086', 'mp-25014', 'mp-19321']
list5 = ['mp-7831', 'mp-16293', 'mp-3653', 'mp-29910', 'mp-29455', 'mp-25043', 'mp-10486', 'mp-5909', 'mp-22937', 'mp-29606', 'mp-2951']
list6 = ['mp-4590', 'mp-541368', 'mp-27684', 'mp-22734', 'mp-7461', 'mp-20337', 'mp-23419']
list7 = ['mp-5380', 'mp-7863', 'mp-8624', 'mp-3744', 'mp-7502', 'mp-1346', 'mp-20694', 'mp-761872']
sarmandi = ['mp-7233', 'mp-4764', 'mp-13971', 'mp-13973']    # X2SeO2, X= La, Pr, Nd, Gd

zero_gaps = ['mp-13971', 'mp-2045']    # X2SeO2, X=  Pr, Nd, Gd  mp-19079 (zero-gap even on MP)

pTCO_SI_list1 = ['mp-28962', 'mp-13060', 'mp-617']
pTCO_SI_list2 = ['mp-5709', 'mp-18288', 'mp-28711', 'mp-23487']
pTCO_SI_list3 = ['mp-25726', 'mp-3370', 'mp-4086', 'mp-2931', 'mp-17559', 'mp-8111']
TE1 = ['mp-22619', 'mp-486', 'mp-555818', 'mp-2074', 'mp-7955', 'mp-991676', 'mp-9295', 'mp-991652']  # NiP2, NiP2, SiCu2PbS4, Li3Sb, Li3Sb, (Nb-Ta-V)Cu3Te4

famous = ['mp-2133', 'mp-3163', 'mp-22598', 'mp-22323', 'mp-644741'] # 			ZnO, BaSnO3, 3_In2O3 
famous1= ['mp-856', 'mp-550172', 'mp-755071', 'mp-545544', 'mp-23092', 'mp-552200']  #  3_SnO2, 3_Ba2TaBiO6
	
# mp-21905, mp-3331 and mp-29047 don't exist on MP website
so_list = ['mp-8298', 'mp-8299', 'mp-7787', 'mp-19845', 'mp-8789', 'mp-3519']
#	materials_list = list1 + list2 + list3 + list4 + list5 + list6 + list7
materials_list = list2 + list3 + list4 + list5 + list6 + list7 + sarmandi + pTCO_SI_list1 + pTCO_SI_list2 + pTCO_SI_list3 + so_list + zero_gaps + famous + famous1

jobs = ['geom', 'self', 'nself', 'nself_aMoBT', 'phonon', 'dielectric']
import os

with file('incomplete_jobs.txt', 'w') as incmplt:
	for id in materials_list:
		if os.path.exists(id):
			os.chdir(id)
			for j in jobs:
				if os.path.exists(j):
					os.chdir(j)
					if os.path.isfile("OUTCAR"):
						if "Voluntary context switches:" not in open('OUTCAR').read():
							incmplt.write(os.getcwd() + ' \n')
					else:
						incmplt.write(os.getcwd() + ' \n')
					os.chdir("../")
			os.chdir("../")
