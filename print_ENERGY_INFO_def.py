#!/usr/bin/env python
# Written by Alireza Faghaninia (alireza@wustl.edu)
# This code might return the following warning which can be ignored and it's due to calling a MATLAB function: "error: scalar cannot be indexed with ."


import os

def find_reference(scripts_path):
        os.system("cp " + scripts_path + "find_eval_eband.m .")
#       os.system('cp ./nself_aMoBT/EIGENVAL .')
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

if __name__ == "__main__":	
	scripts_path = '~/scripts/dekode_scripts/'
	strain = [-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
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

