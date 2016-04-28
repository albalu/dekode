#!/usr/bin/env python
# This code will analyze the data that is collected via collect_data.py and store them in a matrix for analysis
# Please contact alireza@wustl.edu if you had any questions. Bug reports are very much appreciated.
# By: Alireza Faghaninia


from __future__ import division
import os
import numpy as np


def evaluate_effmass(data,exceptions,m,k):  # m and k are the column number in the matrix of data orders of which wanted to be compared
	norder = 0
	n = len(data)
	for i in range(0,n-1):
		for j in range(i+1,n):
			if (i+1 not in exceptions) and (j+1 not in exceptions):
				if float(data[i,k]) >= float(data[j,k]):
					if float(data[i,m]) > float(data[j,m]):
						norder += 1
#						print(data[i,m])
#						print(data[i,k])
				else:
					if float(data[i,m]) <= float(data[j,m]):
						norder += 1
#			else:
#				print(str(i) + '   ' + str(j) + ' \n')
	print(norder)
	n = n - len(exceptions)
	print(n*(n-1)/2)
	print(n)
	accuracy = float(1 - norder/(n*(n-1)/2))
	return accuracy

scripts_path = '~/scripts/dekode_scripts/'

data_list = []

with open('DATA_ALL.txt', 'r') as raw_data:
	counter = 0
	for line in raw_data:
		counter += 1
		if counter > 1:
#			'%15s %15.2f %22.4f %22.4f %15.2f %15.2f %15.2f %15.4f %15.4f' % (material_id, band_gap, n_cond, p_cond, LO_phonon, epsilon_0, epsilon_inf, electron_mass, hole_mass) = line.split()
#			'%s %f %f %f %f %f %f %f %f' % (material_id, band_gap, n_cond, p_cond, LO_phonon, epsilon_0, epsilon_inf, electron_mass, hole_mass) = line.strip()
			(material_id, band_gap, n_cond, p_cond, LO_phonon, epsilon_0, epsilon_inf, electron_mass, hole_mass) = line.split()
#			band_gap, n_cond, p_cond, LO_phonon, epsilon_0, epsilon_inf, electron_mass, hole_mass = map(float, (band_gap, n_cond, p_cond, LO_phonon, epsilon_0, epsilon_inf, electron_mass, hole_mass))
			data_list.append([counter-1, band_gap, n_cond, p_cond, LO_phonon, epsilon_0, epsilon_inf, electron_mass, hole_mass])
	data = np.mat(data_list)
#	print(data)	

	exceptions = [17, 24, 25, 32, 43, 44, 45, 51, 57, 74, 75]
#	exceptions = []
# List of excluded ID's:
#	mp-566788
#	mp-19148
#	mp-1705
#	mp-19006
#	mp-25014
#	mp-19321
#	mp-19079 
#	mp-25043
#	mp-4590
#	mp-7787
#	mp-19845

	e_accuracy = evaluate_effmass(data,exceptions,2,7)

	exceptions = [7, 10, 17, 24, 25, 29, 32, 33, 35, 36, 40, 43, 44, 45, 51, 57]
#	exceptions = []
# List of excluded ID's:
#	mp-31132
#	mp-3443
#	mp-566788
#	mp-19148
#	mp-1705
#	mp-27175
#	mp-19006
#	mp-3056
#	mp-8922
#	mp-7762
#	mp-540688
#	mp-25014
#	mp-19321
#	mp-19079
#	mp-25043
#	mp-4590

	h_accuracy = evaluate_effmass(data,exceptions,3,8)

#	if int(data[3,0]) not in exceptions:
#		print('nooooooo')

### Check to see if the order of electron effective mass and mobility are the same
#	print(norder)
#	print(n*(n-1)/2)
	print('accuracy for electron effective mass = %4.2f ' % e_accuracy)
	print('accuracy for hole effective mass = %4.2f ' % h_accuracy)
	print(data.shape)

#	x1 = sorted(data_list,key=lambda x:float(data_list[1],reverse = True)
#	print(x1)

	# Maximum band gap
#	print(data[1,np.argmax(data, axis=1)[1]])
#	print(data[4,:].argmax())

#	eqidx = np.where(data[:,0]==0)[0]
#	eqidx = abs(int(data[0,0])) + 1
#	eqvol = data[eqidx,1]

