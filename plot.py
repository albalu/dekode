#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from decimal import *
import os

os.system("cp ./self/OUTCAR ./nself/EIGENVAL .")
os.system("cp ~/dekode/plot_bandstructure2.m .")
os.system("octave -q --eval plot_bandstructure2.m")

while os.path.isfile("axis.mat")== "FALSE":
    pass

i = 0
X = []
Y = []
Z = []
with open('axis.mat','rU') as axis:
    for line in axis:
        i = i + 1
        if i<6:
            pass
        else:
            line = line.strip()
            if line != '':
                line = Decimal(str(line))
                X = X+[line]

k = 0
with open('bands.mat','rU') as bands:
    for bline in bands:
        k = k + 1
        if k == 7:
            end = bline.split("\n")
            end = end[0]
            end = end.split()
            number_of_bands = len(end)
        elif k>7:
           break

for j in np.linspace(0,number_of_bands-1,number_of_bands):
    Z = []
    j = int(j)
    l = 0
    with open('bands.mat','rU') as bands:
            for line in bands:
                l = l + 1
                if l<6:
                    pass
                else:
                    line = line.split("\n")
                    line = line[0]
                    if line != '':
                        line = line.split()[j]
                        lin = Decimal(str(line))
                        Z = Z+[lin]
    plt.plot(X,Z)

#plt.show()
plt.savefig('bandstructure.png')

os.system("rm *.mat OUTCAR EIGENVAL plot_bandstructure2.m")
