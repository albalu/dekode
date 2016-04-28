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
aMoBT_path = "/research-projects/partita/faghaniniaa/current_jobs/carrier_scattering/VERSIONS/latest_aMoBT/"
scripts_path = "~/scripts/dekode_scripts"

with open('MIKECAR', "r") as f:
    for line in f:
        line = line.split()
        if line[0] == "EMAIL":
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
        elif line[0] == "PHONON":
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
	elif line[0] == "AMOBT_PATH":
		aMoBT_path = line[2]
	elif line[0] == "SCRIPTS_PATH":
		scripts_path = line[2]

if ~aMoBT_path.endswith('/'):
	aMoBT_path = aMoBT_path + '/'
if ~scripts_path.endswith('/'):
	scripts_path = scripts_path + '/'

####################################

os.system('cp ' + scripts_path + 'run_aMoBT.py .')
os.system('cp ' + scripts_path + 'find_eval_eband.m .')
from run_aMoBT import generate_aMoBT_input
from run_aMoBT import find_reference


################ Set up nested functions to be used later ##################

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

def get_POTCAR():
    c = 0
    with open('POSCAR', "rU") as f:
        for line in f:
            c = c + 1
            if c == 6:
                compound = line.split()
                num = range(len(compound))
            elif c > 6:
                break

    echoline = "cat "
    for i in num:
        if os.path.isfile("/cluster/caml/vasp-pot/PBE/"+compound[i]+"/POTCAR"):
            echoline += "/cluster/caml/vasp-pot/PBE/"+compound[i]+"/POTCAR "
        elif os.path.isfile("/cluster/caml/vasp-pot/PBE/"+compound[i]+"_d/POTCAR"):
            echoline += "/cluster/caml/vasp-pot/PBE/"+compound[i]+"_d/POTCAR "
        elif os.path.isfile("/cluster/caml/vasp-pot/PBE/"+compound[i]+"_sv/POTCAR"):
            echoline += "/cluster/caml/vasp-pot/PBE/"+compound[i]+"_sv/POTCAR "
        elif os.path.isfile("/cluster/caml/vasp-pot/PBE/"+compound[i]+"_h/POTCAR"):
            echoline += "/cluster/caml/vasp-pot/PBE/"+compound[i]+"_h/POTCAR "
        elif os.path.isfile("/cluster/caml/vasp-pot/PBE/"+compound[i]+"_s/POTCAR"):
            echoline += "/cluster/caml/vasp-pot/PBE/"+compound[i]+"_s/POTCAR "
        elif os.path.isfile("/cluster/caml/vasp-pot/PBE/"+compound[i]+"_pv/POTCAR"):
            echoline += "/cluster/caml/vasp-pot/PBE/"+compound[i]+"_pv/POTCAR "
        elif os.path.isfile("/cluster/caml/vasp-pot/PBE/"+compound[i]+"_GW/POTCAR"):
            echoline += "/cluster/caml/vasp-pot/PBE/"+compound[i]+"_GW/POTCAR "

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


replace('INCAR_NSELF', 'INCAR_NSELF', 'NBANDS = 100', '')
