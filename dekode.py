#!/usr/bin/env python

# This file runs the geometric optization, self consistent, and non-self
# consitent calculations for a given material

# To set up this file properly, create a new directory for this material, and
# make sure the following files are present: POTCAR, POSCAR, KPOINTS, 
# KPOINTS_NSELF, KPOINTS_aMoBT, MIKECAR, vasp-__.csh
# Where: KPOINTS_NSELF is the KPOINTS file to be used for the nself step
# KPOINTS_aMoBT is the KPOINTS file to be used for the dense mesh for the a MoBT nself calculation

import os
import time
from time import sleep
import smtplib
from decimal import *
import re
from tempfile import mkstemp
from shutil import move
from decimal import *
from os import remove, close
import urllib2
import json as jsonlib

# test!
# test!

import pymatgen as mp
from pymatgen.symmetry.bandstructure import HighSymmKpath


########### READ SETTINGS FROM MIKECAR ############
# The default settings are to run just the geom, self, and nself steps
# They will only be overwritten if the MIKECAR file has proper formatting
# to change these, just change the initial definitions of the variables below

contact = "caml.alert@gmail.com"
name = "JOB NAME"
geom = "FALSE"
self = "FALSE"
nself = "FALSE"
nself_aMoBT = "FALSE"
dielectric = "FALSE"
phonon = "FALSE"
dim = "1 1 1"
deform = "FALSE"
strain = "-5,6"
poscar = "default"
incar = "default"
aMoBT = "FALSE"
SOC = "False"
aMoBT_path = "/research-projects/partita/faghaniniaa/current_jobs/carrier_scattering/VERSIONS/latest_aMoBT/"
scripts_path = "~/dekode"
potcar_patj = "/cluster/caml/vasp-pot/PBE/"
computer = 'partita'

with open('MIKECAR', "r") as f:
    for line in f:
        line = line.split()
        if line[0] in ["email", "Email", "EMAIL"]:
            contact = line[2]
        if line[0] == "COMP_NAME":
            comp_name = line[2]
        elif line[0] == "POSCAR":
            poscar = line[2]
        elif line[0] == "INCAR":
            incar = line[2]
        elif line[0] == "JOB_NAME":
            name = line[2]
        elif line[0] == "GEOM":
            geom = line[2]
        elif line[0] == "SELF":
            self = line[2]
        elif line[0] == "NSELF":
            nself = line[2]
        elif line[0] == "NSELF_AMOBT":
            nself_aMoBT = line[2]
        elif line[0] == "DIEL":
            dielectric = line[2]
        elif line[0] in ["phonon", "Phonon", "PHONON"]:
            phonon = line[2]
        elif line[0] == "DIM":
            dim = line[2]
            dim = re.sub("[^0-9]"," ", dim)
        elif line[0] == "DEFORM":
            deform = line[2]
        elif line[0] == "RANGE":
            strain = line[2]
            strain = strain.split(",")
            strain[1] = int(strain[1])+1
            strain = range(int(strain[0]),strain[1])
	elif line[0] == "MP_API_KEY":
		mp_api_key = line[2]
	elif line[0] == "AMOBT":
		aMoBT = line[2]
	elif line[0] == "POTCAR_PATH":
		potcar_path = line[2]
	elif line[0] == "AMOBT_PATH":
		aMoBT_path = line[2]
	elif line[0] == "SCRIPTS_PATH":
		scripts_path = line[2]
	elif line[0] == "SOC":
		SOC = line[2]
	elif line[0] == "COMPUTER":
		computer = line[2]

if not potcar_path.endswith('/'):
	potcar = potcar_path + '/'
if not aMoBT_path.endswith('/'):
	aMoBT_path = aMoBT_path + '/'
if not scripts_path.endswith('/'):
	scripts_path = scripts_path + '/'

####################################

os.system('cp ' + scripts_path + 'run_aMoBT.py .')
os.system('cp ' + scripts_path + 'find_eval_eband.m .')
from run_aMoBT import generate_aMoBT_input
from run_aMoBT import find_reference


################ Set up nested functions to be used later ##################

def run_vasp(computer = 'partita', y = 'vasp-ib2.csh', ncores = 16):
	if computer in ['edison', 'Edison', 'EDISON']:
		ncores = 12
	if computer in ['partita', 'Partita', 'PARTITA']:
		os.system('qsub ' + y)
	elif computer in ['cori', 'Cori', 'CORI', 'edison', 'Edison', 'EDISON']:
		os.system('srun -n ' + str(ncores) + ' vasp_std')
	return

# This function returns the length of a file
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

# This function sends and email to the user
def alert(error,recipient):
        content = error
        mail = smtplib.SMTP('smtp.gmail.com',587)
        mail.ehlo()
        mail.starttls()
        mail.login('caml.wustl@gmail.com','Wav3function')
        mail.sendmail('caml.wustl@gmail.com',recipient,content)
        mail.close()

#this function returns the length of a file
def file_len(fname):
   count = 0
   f = open(fname)
   for line in f:
        count = count + 1
   return count

def get_POTCAR(potcar_path, potcar_labels = ''):
	echoline = "cat "
	if potcar_labels == '':
		c = 0
		with open('POSCAR', 'r') as f:
			for line in f:
				c += 1
				if c == 6:
					potcar_labels = line.split()
				elif c > 6:
					break
	print(potcar_labels)
	for label in potcar_labels:
		if os.path.isfile(potcar_path + label + '/POTCAR'):
			echoline += potcar_path + label + '/POTCAR '
		elif os.path.isfile(potcar_path + label + '_d' + '/POTCAR'):
			echoline += potcar_path + label + '_d' + '/POTCAR '
		elif os.path.isfile(potcar_path + label + '_sv' + '/POTCAR'):
			echoline += potcar_path + label + '_sv' + '/POTCAR '
		elif os.path.isfile(potcar_path + label + '_h' + '/POTCAR'):
			echoline += potcar_path + label + '_h' + '/POTCAR '
		elif os.path.isfile(potcar_path + label + '_s' + '/POTCAR'):
			echoline += potcar_path + label + '_s' + '/POTCAR '
		elif os.path.isfile(potcar_path + label + '_pv' + '/POTCAR'):
			echoline += potcar_path + label + '_pv' + '/POTCAR '
		elif os.path.isfile(potcar_path + label + '_GW' + '/POTCAR'):
			echoline += potcar_path + label + '_GW' + '/POTCAR '
	echoline += " > POTCAR"
	os.system(echoline)


def wait_for_OUTCAR(step):
    x=1
    emin = 0
    count=0
    line='1'
    while x==1:
        if os.path.isfile("OUTCAR"):
            fp = open("OUTCAR")
            for line in fp:
                line = line.split()
            if emin == 0:
                a = file_len('OUTCAR')
            if len(line)>1:
                if line[0]=='Voluntary':
                    x=0
                else:
                    emin = emin+1    
                    sleep(60)
            if emin == 60:
                if file_len('OUTCAR') == a:
                    alert("Your job: " + name + " failed during the " + step + " step",contact)
                    quit()
                else:
                    emin = 0
def replace(file,newfile,pattern,subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with open(abs_path,'w') as new_file:
        with open(file) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    close(fh)
    #Move new file
    move(abs_path, newfile)

def check_OUTCAR(i):
    if os.path.isfile("OUTCAR"):
        fp = open("OUTCAR")
        for line in fp:
            line = line.split()
            if len(line)>2:
                if line[0]=='Voluntary':
                    done[i] = 1

def Ksplit():
    with open('KPOINTS') as f:
        for i, l in enumerate(f):
            pass
    end = i + 1

    count = 0
    point = ['','','','']
    with open('KPOINTS', "rU") as f:
        for line in f:
            count = count + 1
            if count < 6:
                pass
            elif count == end:
                print count
                print "OK"
                print end
                break
            else:
                line = line.split()
                if line != [''] and len(line) == 5:
                    point[0] = line[4]
                    point[3] = point[2]
                    point[2] = point[1]
                    point[1] = point[0]
                if point[0] == point[1] and point[2] == point[3]:
                    pass
                elif point[1] == point[2] and point[0] != point[3]:
                    pass
                else:
                    print count
                    break
                print point
    num = 0
    with open('KPOINTS', "rU") as f:
        for line in f:
            num = num + 1
            if num < count:
                h = open('New','a')
                h.write(line)
    h.write('\n')
    os.system('mv New KPOINTS')

def get_INCARs(comp_name, mp_api_key, SOC):
    from pymatgen.matproj.rest import MPRester
    matproj = MPRester(mp_api_key)

    structure = matproj.get_structure_by_material_id(comp_name)
    from pymatgen.io.vasp.sets import MPVaspInputSet
    from pymatgen.io.vasp.sets import MPGGAVaspInputSet   # +U is turned off (if any)
    from pymatgen.io.vasp.sets import MPHSEVaspInputSet
    from pymatgen.io.vasp.sets import MPStaticVaspInputSet
    from pymatgen.io.vasp.sets import MPNonSCFVaspInputSet
    from pymatgen.io.vasp.sets import MPStaticDielectricDFPTVaspInputSet
    from pymatgen.io.vasp.sets import MPBSHSEVaspInputSet
    from pymatgen.io.vasp.sets import MPOpticsNonSCFVaspInputSet

    v = MPVaspInputSet()
    indic = v.get_incar(structure)
    k = v.get_all_vasp_input(structure,generate_potcar = False)
    incar_file = open('INCAR','w')
    if SOC in ['TRUE', 'True', 'true']:
	indic['LMAXMIX'] = 4
	indic['NBANDS'] = 128
	indic['LSORBIT'] = '.TRUE.'
	indic.pop('MAGMOM', None)
    incar_file.write(str(indic))

    self = MPStaticVaspInputSet()
    indic = self.get_incar(structure)
    indic['NEDOS'] = 9001
    incar_file = open('INCAR_SELF','w')
    if SOC in ['TRUE', 'True', 'true']:
	indic['LMAXMIX'] = 4
	indic['NBANDS'] = 128
	indic['LSORBIT'] = '.TRUE.'
	indic.pop('MAGMOM', None)
    incar_file.write(str(indic))

    user_incar_settings = {"NBANDS" : 100}
    nself = MPNonSCFVaspInputSet(user_incar_settings)
    indic = nself.get_incar(structure)
    incar_file = open('INCAR_NSELF','w')
    if SOC in ['TRUE', 'True', 'true']:
	indic['LMAXMIX'] = 4
	indic['NBANDS'] = 128
	indic['LSORBIT'] = '.TRUE.'
	indic.pop('MAGMOM', None)
    incar_file.write(str(indic))

    HSE = MPHSEVaspInputSet()
    indic = HSE.get_incar(structure)
    incar_file = open('INCAR_HSE','w')
    if SOC in ['TRUE', 'True', 'true']:
	indic['LMAXMIX'] = 4
	indic['NBANDS'] = 128
	indic['LSORBIT'] = '.TRUE.'
	indic.pop('MAGMOM', None)
    incar_file.write(str(indic))




############################################################################



############### Write in the different INCAR files needed for the calculations #####################################

# These functions write the INCAR files for the different steps of the code
# You can change the INCAR files by changing these definitions

def writeINCARgeom(SOC = 'False'):
    h = open('INCAR','w')
    h.write("ALGO = Normal\n")
    h.write("EDIFF = 0.00001\n")
    h.write("ENCUT = 520\n")
    h.write("IBRION = 2\n")
    h.write("ICHARG = 0\n")
    h.write("ISIF = 3\n")
    h.write("ISMEAR = -5\n")
    h.write("ISPIN = 2\n")
    h.write("LORBIT = 11\n")
    h.write("LREAL = .FALSE.\n")
    h.write("LWAVE = False\n")
    h.write("NELM = 100\n")
    h.write("NSW = 99\n")
    h.write("PREC = Accurate\n")
    h.write("SIGMA = 0.2\n")
    if SOC in ['TRUE', 'True', 'true']:
	h.write('LMAXMIX = 4\n')
	h.write('NBANDS = 128\n')
	h.write('LSORBIT = .TRUE.')
    h.close()

def writeINCARself(SOC = 'False'):
    h = open('INCAR','w')
    h.write("ALGO = Normal\n")
    h.write("EDIFF = 0.00001\n")
    h.write("ENCUT = 520\n")
    h.write("IBRION = -1\n")
    h.write("ICHARG = 2\n")
    h.write("ISMEAR = -5\n")
    h.write("ISPIN = 2\n")
    h.write("LORBIT = 11\n")
    h.write("LREAL = .FALSE.\n")
    h.write("LWAVE = .TRUE.\n")
    h.write("LCHARG = .TRUE.\n")
    h.write("NEDOS = 9001\n")
    h.write("NELM = 100\n")
    h.write("NSW = 0\n")
    h.write("PREC = Normal\n")
    h.write("SIGMA = 0.2\n")
    if SOC in ['TRUE', 'True', 'true']:
	h.write('LMAXMIX = 4\n')
	h.write('NBANDS = 128\n')
	h.write('LSORBIT = .TRUE.')
    h.close()

def writeINCARnself(SOC = 'False'):
    h = open('INCAR','w')
    h.write("ALGO = Normal\n")
    h.write("EDIFF = 0.00001\n")
    h.write("ENCUT = 520\n")
    h.write("IBRION = -1\n")
    h.write("ICHARG = 11\n")
    h.write("ISPIN = 2\n")
    h.write("LORBIT = 11\n")
    h.write("LREAL = .FALSE.\n")
    h.write("LWAVE = .FALSE.\n")
    h.write("LCHARG = .FALSE.\n")
    h.write("NELM = 100\n")
    h.write("NSW = 0\n")
    h.write("PREC = Normal\n")
    if SOC in ['TRUE', 'True', 'true']:
	h.write('LMAXMIX = 4\n')
	h.write('NBANDS = 128\n')
	h.write('LSORBIT = .TRUE.')
    h.close()

def writeINCARdielectric():
    h = open('INCAR','w')
    h.write("ENCUT = 520\n")
    h.write("EDIFF = 1E-6\n")
    h.write("LEPSILON = .TRUE.\n")
    h.write("LPEAD = .TRUE.\n")
    h.write("IBRION = 8\n\n")
    h.write("ISMEAR = -5\n")
    h.write("SIGMA = 0.01\n")
    h.write("GGA = PE\n")
    h.close()

def writeINCARphonon():
    h = open("INCAR", "w")
    h.write('# SCF input for VASP'    +'\n')
    h.write('# Note that VASP uses the FIRST occurence of a keyword' +'\n')
    h.write('SYSTEM = (Pb C I3 N H6)4  (P1) ~ POSCAR (VASP)'         +'\n')
    h.write('PREC = Accurate'                                        +'\n')
    h.write('  ENCUT = 520.000'                                      +'\n')
    h.write(' IBRION = 8'                                            +'\n')
    h.write('  EDIFF = 1.0e-08'                                      +'\n')
    h.write('  IALGO = 38'                                           +'\n')
    h.write(' ISMEAR = 0; SIGMA = 0.1'                               +'\n')
    h.write('  LREAL = .FALSE.'                                      +'\n')
    h.write('ADDGRID = .TRUE.'                                       +'\n')
    h.write('  LWAVE = .FALSE.'                                      +'\n')
    h.write(' LCHARG = .FALSE.'                                      +'\n')
    h.write(' ISPIN = 2' 	                                     +'\n')


######################################################################################



####### Identify the correct vasp script to call ##########
y = 'vasp' # default
if os.path.isfile("vasp-gpu.csh")==True:
        y = "vasp-gpu.csh"
if os.path.isfile("vasp-ib2.csh")==True:
        y = "vasp-ib2.csh"
if os.path.isfile("vasp-ib.csh")==True:
        y = "vasp-ib.csh"
if os.path.isfile("vasp-mpi.csh")==True:
        y = "vasp-mpi.csh"
if SOC in ['TRUE', 'True', 'true']:
	os.system('cp ~/vasp53_spin-orbit-coupling.mpi .')
	y = 'vasp53_spin-orbit-coupling.mpi'

############################################################

######################  write POSCAR, POTCAR, KPOINTS, KPOINTS_NSELF ##################

if (poscar == "default") and ((geom in ['t', 'T', 'TRUE', 'True', 'true']) or (nself in ['t', T', 'TRUE', 'True', 'true'])):
    matproj = mp.MPRester(mp_api_key)
    structure = matproj.get_structure_by_material_id(comp_name)
    structure.to(filename="POSCAR")

    dum = matproj.query(criteria=comp_name, properties=["potcar_symbols","potcar_spec","pseudo_potential"])
    potcar_labels = dum[0]["pseudo_potential"]["labels"]
    get_POTCAR(potcar_path, potcar_labels)

    geom_kpoints = mp.io.vasp.inputs.Kpoints.automatic_density(structure,1000,force_gamma=False)
    mp.io.vasp.inputs.Kpoints.write_file(geom_kpoints,'KPOINTS')

    nself_kpoints = mp.io.vasp.inputs.Kpoints.automatic_linemode(20,mp.symmetry.bandstructure.HighSymmKpath(structure, symprec=0.01, angle_tolerance=5))
    mp.io.vasp.inputs.Kpoints.write_file(nself_kpoints,'KPOINTS_NSELF')

if incar == "default":
    get_INCARs(comp_name, mp_api_key, SOC)

#  Send an email to the user letting them know that sully.py has started to run
# for some reason the emails were empty hence the ### at the beginning of the next line
### alert('Your job: ' + name + ' has started',contact) 

############ GEOMETRIC OPTIMIZATION #########################################################################################

if geom in ['TRUE', 'True', 'true']:
	if incar != "default":
	        writeINCARgeom(SOC)
#	if (~os.path.exists('POTCAR')) or (os.stat('POTCAR').st_size == 0):
	get_POTCAR(potcar_path)

# Make a directory for the files involved in the geometric optimization
	os.system("mkdir geom")
	os.system("cp "+y+" geom/")
	os.system("mv INCAR KPOINTS POSCAR POTCAR geom/")
	os.chdir("geom/")    

# Now submit the first the job for the first time for geometric optimization
	run_vasp(computer, y)
	wait_for_OUTCAR('geom')
	os.chdir("../")

######################################################################################################################################################



############################### SELF CONSISTENT CALCULATIONS #################################################################

if self in ['t', 'T', 'TRUE', 'True', 'true']:

    # write proper INCAR file
    if incar != "default":
        writeINCARself(SOC)
    else:
        os.system("mv INCAR_SELF INCAR")
    # retreive the files needed form the geom step from the geom directory
    os.system("cp ./geom/KPOINTS .")
    os.system("cp ./geom/CONTCAR .")
    os.system("cp ./geom/POTCAR .")
    os.system("mv CONTCAR POSCAR")

    # Make directory for the files involved with the self consistent calculations
    os.system("mkdir self")
    os.system("cp "+y+" self/")
    os.system("mv INCAR KPOINTS POSCAR POTCAR  self/")
    os.chdir("self/")         

    # Now run the self consistent calculations
    run_vasp(computer, y)

    wait_for_OUTCAR('self')

    os.chdir("../")

###############################################################################################################################


###################### NON-SELF CONSISTENT CALCULATIONS #######################################################################

if nself in ['t', 'T', 'TRUE', 'True', 'true']:

    #write the proper INCAR file
    if incar != "default":
        writeINCARnself(SOC)
    else:
	replace('INCAR_NSELF', 'INCAR_NSELF', 'NBANDS = 100', '')
        os.system("mv INCAR_NSELF INCAR")
    
    
    # Rename KPOINTS_NSELF to KPOINTS so vasp can read it, and retreive the needed files from the self directory
    os.system('cp ./self/POSCAR .')
    os.system('cp ./self/POTCAR .')
    os.system('cp ./self/CHG* .')

    # Make a directory for the files involved with the  non-self consistent calcuations
    os.system("mkdir nself")
    if os.path.exists('KPOINTS_nself'):
	os.system('mv KPOINTS_nself KPOINTS_NSELF')
    try:
    	with open('KPOINTS_NSELF','r') as atest:
		pass
    except IOError:
		raise IOError('KPOINTS_NSELF (line-mode) must be present for the band structure (nself) calculation')

    os.system('mv KPOINTS_NSELF nself/KPOINTS')
    os.system("cp "+y+" nself/")
    os.system("mv POSCAR POTCAR INCAR CHG* nself/")

    os.chdir("nself/")
    Ksplit()

    # Run the non-self consistent calculations
    run_vasp(computer, y)

    wait_for_OUTCAR('nself')

    os.chdir("../")

#########################################################################################################################################################


###################### aMoBT NON-SELF CONSISTENT CALCULATIONS #######################################################################

if nself_aMoBT in ['t', 'T', 'TRUE', 'True', 'true']:

    os.system("cp " + scripts_path +  "KPOINTS_generator_for_aMoBT.m .")
    if os.path.exists('nself/EIGENVAL'):
	    os.system("cp nself/EIGENVAL .")
	    val_kpoint, con_kpoint, eval, econ, core = find_reference(scripts_path)
	    replace("KPOINTS_generator_for_aMoBT.m","KPOINTS_generator_for_aMoBT.m","0 0 0", con_kpoint)

    os.system("octave -q KPOINTS_generator_for_aMoBT.m")
    os.system("rm *.mat")
    os.system("rm EIGENVAL")  

    # Retreieve the needed files from the nself directory and rename KPOINTS_aMoBT to KPOINTS
    os.system('mv KPOINTS_aMoBT KPOINTS')
    os.system('cp ./self/POTCAR .')
    os.system('cp ./self/POSCAR .')
    os.system('cp ./self/CHG* .')
    if os.path.exists('nself'):
	    os.system('cp ./nself/INCAR .')
    else:
	    writeINCARnself(SOC)


    # Make a directory for the files involved with the  non-self consistent calcuations
    os.system("mkdir nself_aMoBT")
    os.system("mv KPOINTS INCAR POTCAR POSCAR CHG* nself_aMoBT/")
    os.system("cp "+y+" nself_aMoBT/")

    os.chdir("nself_aMoBT/")

    # Run the non-self consistent calculations
    run_vasp(computer, y)


    if os.path.exists('nself/EIGENVAL'):
    	if val_kpoint != con_kpoint:
		os.chdir("../")
		replace("KPOINTS_generator_for_aMoBT.m","KPOINTS_generator_for_aMoBT.m", con_kpoint, val_kpoint)
		os.system("octave -q KPOINTS_generator_for_aMoBT.m")
		os.system('cp -r nself_aMoBT p_nself_aMoBT')
		os.system('mv KPOINTS_aMoBT p_nself_aMoBT/KPOINTS')
		os.chdir("p_nself_aMoBT")
        	run_vasp(computer, y)
		wait_for_OUTCAR('p_nself_aMoBT')
		os.chdir("../nself_aMoBT")

    wait_for_OUTCAR('nself_aMoBT')

    os.chdir("../")
##############################################################################################################################################################


############################### DIELECTRIC CALCULATIONS #################################################################

if dielectric in ['t', 'T', 'TRUE', 'True', 'true']:

    # Write proper INCAR file
    writeINCARdielectric()

    # Retrieve the needed files from the self directory
    os.system('cp ./self/KPOINTS .')
    os.system('cp ./self/POSCAR .')
    os.system('cp ./self/POTCAR .')

    # Make directory for the files involved with the self consistent calculations
    os.system("mkdir dielectric")
    os.system("cp "+y+" dielectric")
    os.system("mv KPOINTS POSCAR POTCAR INCAR dielectric/")

    os.chdir("dielectric/")
    with open('KPOINTS','r') as k:
	for line in k:
		if line[0] == 'M':
    			replace('KPOINTS','KPOINTS','Monkhorst','Gamma')

    # Now run the self consistent calculations
    run_vasp(computer, y)

    wait_for_OUTCAR('dielectric')

    # This section reads the OUTCAR file and calculates the dielectric constants which will be printed to the terminal or nohup.out
    count = 0
    with open('OUTCAR', "rU") as f:
        for line in f:
            count = count + 1
            lin = line.split()
            if len(lin) > 2:
                if lin[0] == "MACROSCOPIC" and lin[4] == "(including":
                    count = -5
                elif lin[0] == "MACROSCOPIC" and lin[4] == "IONIC":
                    count = -10
            if count == -3:
                x = Decimal(lin[0])
            elif count == -2:
                y_ = Decimal(lin[1])
            elif count == -1:
                z = Decimal(lin[2])
            elif count == -8:
                a = Decimal(lin[0])
            elif count == -7:
                b = Decimal(lin[1])
            elif count == -6:
                c = Decimal(lin[2])
                count = 0
    static = (x + y_ + z)/3
    high_freq = static - (a + b + c)/3
    print "Average Static Dielectric Constant = " + str(round(static,3))
    print "High Frequency Dielectric Constant = " + str(round(high_freq,3))

    os.chdir("../")

###############################################################################################################################

############################# PHONON CALCULATIONS #############################################################################

if phonon in ['t', 'T', 'TRUE', 'True', 'true']:

    #steps to run code.py after finishing band:
    #1 (make and navigate to phonon folder)
    #2 module load software-2014
    #3 (copy code.py to the otherwise empty phonon folder)
    #4 nohup python code.py
    #- (perform steps 5 and 6 on a computer capable of plotting with Xming)
    #5 phonopy -p mesh.conf -c POSCAR-unitcell
    #6 phonopy -p band.conf -c POSCAR-unitcell
    #7 (get max phonon frequency)
    #8 (make and navigate to dielectric folder)
    #9 (copy over INCAR_dielectric, geom's KPOINTS, band's POSCAR POTCAR vasp-ib2.csh)
    #10 (submit dielectric job)
    #11 grep -10n STATIC OUTCAR (in dielectric)
    #12 (use trace of matrix(1) for static, matrix(1)-matrix(3) for high freq)
    
    #to begin, make a phonon folder among band/geom/dos folders and navigate to it
    #run "module load software-2014"
    #call with: " nohup python code.py & "
    #to kill job: " pkill -f code.py "
    #when killing job, check if job is still submitted to node
    
    os.system("mkdir phonon")
    os.chdir("phonon/")
    ###copy###
    os.system('cp ../nself/POSCAR .')
    os.system('cp ../geom/KPOINTS .')
    os.system('cp ../nself/POTCAR .')
    os.system('cp ../'+y+' .')
    kgrid_ints = [int(i) for i in dim if i.isdigit()]
    with open('new_KPOINTS','w') as new_kp:
	with open('KPOINTS','r') as kp:
		counter = 0
		for line in kp:
			counter += 1
			if counter == 4:
				(a, b, c) = [int(i) for i in line.split()]
				new_kp.write('%2d %2d %2d' % (int(a/kgrid_ints[0]), int(b/kgrid_ints[1]), int(c/kgrid_ints[2])))
			else:
				new_kp.write(line)
    os.system('mv new_KPOINTS KPOINTS')


    ###copy###
    writeINCARphonon()
    ###mesh###
    fp = open("POSCAR")
    for i, line in enumerate(fp):
        if i == 5:
            atom_name = line.split('\n')
        elif i>6:
            break
    
    with open("mesh.conf", "wt") as fout:
        fout.write('ATOM_NAME = ' + atom_name[0]            +'\n')
        fout.write('DIM = ' + dim                           +'\n')
        fout.write('MP = 7 7 7'                             +'\n')
        fout.write('FORCE_CONSTANTS = READ'                 +'\n')
        fout.write('DOS = .TRUE.'                           +'\n')
    ###mesh###
    ###band###
    text=''
    count=0
    line1=''
    
    fp = open("../nself/KPOINTS")
    for line in fp:
        if count>3:
            line1=line.split('\n')[0]
            if count==5:
                text=text+line1.split('!')[0]+'  '
            if (count+1)%3!=0:
                if line1!='':
                    text=text+line1.split('!')[0]+'  '
            line0=line1
        count=count+1
    
    with open("band.conf", "wt") as fout:
        fout.write('ATOM_NAME = ' + atom_name[0]            +'\n')
        fout.write('DIM = ' + dim                           +'\n')
        fout.write('BAND_POINTS = 101'                      +'\n')
        fout.write('BAND = ' + text                         +'\n')
        fout.write('FORCE_CONSTANTS = READ'                 +'\n')
    ###band###
    ###phonopy###
    os.system('phonopy -d --dim="'+dim+'"')
    sleep(.1)
    
    x=1
    while x==1:
        if os.path.isfile("SPOSCAR"):
    	    x=0
        else:	
    	    sleep(.1)
    
    os.system('rm POSCAR-*')
    os.system('mv POSCAR POSCAR-unitcell')
    os.system('mv SPOSCAR POSCAR')
    ###phonopy###
    ###submit###
    run_vasp(computer, y)

    wait_for_OUTCAR('phonopy')


    ###submit###
    ###phonopy###
    
    os.system('phonopy --fc vasprun.xml -c POSCAR-unitcell')
    sleep(.1)
    x=1
    while x==1:
        if os.path.isfile("FORCE_CONSTANTS"):
            x=0
        else:
            sleep(.1)

    #final steps:
    #cannot plot mesh and band on laptop, so this is a separate step until I can make X work
    
    os.system("phonopy -c POSCAR-unitcell  mesh.conf")
    os.system("phonopy -c POSCAR-unitcell  band.conf")

    sleep(10)    
    ###phonopy###
    
    os.chdir("../")
    
    

###############################################################################################################################


########################################DEFORMATION CALCULATIONS###############################################################

if deform in ['t', 'T', 'TRUE', 'True', 'true']:

    os.system("mkdir deform")
    os.system("cp self/INCAR .")
    os.system("cp self/POSCAR .")
    os.system("cp self/POTCAR .")
    os.system("cp self/KPOINTS .")
    os.system("cp "+y+" deform/")
    os.system("mv KPOINTS POSCAR POTCAR INCAR deform/")
    os.chdir("deform/")

    length = len(strain)
    os.system("mv POSCAR POSCAR_unstrained")
    
    count = 0
    with open('POSCAR_unstrained', "rU") as f:
        for line in f:
            count = count + 1
            if count == 3:
               first = line
            elif count == 4:
               second = line
            elif count == 5:
               third = line
            elif count > 5:
               break
    list  = [first,second,third]
    
    new = [0,0,0]
    done = []
    finish = []
    for i in strain:
        os.system("mkdir part" + str(i))
        factor = Decimal(i*.01+1)
        for j in list:
            for a in range(3): new[a] =str(Decimal(j.split()[a])*factor)
            h = '   '.join(new)
            if j == first:
                replace('POSCAR_unstrained','POSCAR',first,"    "+h+"\n")
            else:
                replace('POSCAR','POSCAR',j,"   "+h+"\n")
            os.system("cp KPOINTS POSCAR POTCAR INCAR " + y +"  part" + str(i) + "/")       
       
    for i in strain:
        os.chdir("part"+str(i)+"/")
	run_vasp(computer, y)
        os.chdir("../")
        done = done + [0]
        finish = finish + [1]
    
    while finish != done:
        for i in range(len(strain)):
            if done[i] == 0:
                os.chdir("part"+str(i+strain[0])+"/")
                check_OUTCAR(i)        
                os.chdir("../")    
    
    VBM = [0]
    CBM = [0]
#    enfo = open('ENERGY_INFO.txt','w')
    with open('ENERGY_INFO.txt','w') as enfo:
	    enfo.write('%15s %15s %15s %15s %15s %15s \n' % ('strain(%)','volume(A3)','total(eV)','core(eV)','VBM(eV)','CBM(eV)'))
	    for i in strain:
	        os.chdir("part"+str(i)+"/")
		val_kpoint, con_kpoint, eval, econ, core = find_reference(scripts_path)
	        fp = open("OUTCAR")
	        for line in fp:
			line = line.split()
			if len(line)>3:
				if line[0]=='volume':
					vol = float(line[4])
				elif line[0]=='free':
					TOTEN = float(line[4])
		enfo.write('%15d %15.4f %15.4f %15.4f %15.4f %15.4f \n' % (i, vol, TOTEN, core, eval, econ))
		os.chdir("../")

    os.chdir("../")


##############################################################################################################################

if aMoBT in ['t', 'T', 'TRUE', 'True', 'true']:

	from run_aMoBT import run_aMoBT_on_dekode_results
#	run_aMoBT_on_dekode_results(scripts_path, aMoBT_path)	
	run_aMoBT_on_dekode_results(scripts_path, aMoBT_path, T_array = '[150 200 250 300 350 400 450 500 550 600 650 700 750 800]', n_array = '[1e17 1e18 1e19 1e20 1e21]', free_e = 'both')

##############################################################################################################################


# Email user that the job has finished
# for some reason the emails were empty hence the ### at the beginning of the next line
###alert("Your job: " + name + " has finished without error",contact)
