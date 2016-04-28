#!/usr/bin/env python
# This code will sort the TCO data in DATA_ALL.txt file based on conductivity
# Please contact alireza@wustl.edu if you had any questions. Bug reports are very much appreciated.
# By: Alireza Faghaninia

import os
import numpy as np

data_list=[]
with open('DATA_ALL.txt', 'r') as raw_data:
	counter = 0
	for line in raw_data:
		counter += 1
		if counter > 1:
			(material_id, formula, band_gap, n_cond, p_cond, LO_phonon, epsilon_0, epsilon_inf, electron_mass, hole_mass, time) = line.split()
#			band_gap, n_cond, p_cond, LO_phonon, epsilon_0, epsilon_inf, electron_mass, hole_mass = \
#			map(float, (band_gap, n_cond, p_cond, LO_phonon, epsilon_0, epsilon_inf, electron_mass, hole_mass))
			data_list.append([counter-1, band_gap, n_cond, p_cond, LO_phonon, epsilon_0, epsilon_inf, electron_mass, hole_mass])
	data = np.mat(data_list)
#	j = data[[1,3,0],2]
	cond = list(np.array(data[:,2]).reshape(-1))
	print(cond)
	cond = map(float, cond)
	idx = sorted(range(len(cond)), key=lambda k: cond[k])
	idx = np.array(idx)
#	cond_new = np.array(data[:,2])
#	print(np.array(idx))
#	print(cond_new[np.array(idx)])

	sorted_data = data[idx,:]
	print(sorted_data)
