#!/usr/bin/env python
# -*- coding=utf-8 -*-
# code based on http://gvallver.perso.univ-pau.fr/?p=587

import sys
import numpy as np
import os
import argparse

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.gridspec import GridSpec

from pymatgen.io.vasp.outputs import Vasprun, Procar
from pymatgen.symmetry.bandstructure import HighSymmKpath
from pymatgen.electronic_structure.core import Spin, Orbital, OrbitalType

def rgbline(ax, k, e, red, green, blue, alpha=1.):
    # creation of segments based on
    # http://nbviewer.ipython.org/urls/raw.github.com/dpsanders/matplotlib-examples/master/colorline.ipynb
    pts = np.array([k, e]).T.reshape(-1, 1, 2)
    seg = np.concatenate([pts[:-1], pts[1:]], axis=1)

    nseg = len(k) - 1
    r = [0.5 * (red[i] + red[i + 1]) for i in range(nseg)]
    g = [0.5 * (green[i] + green[i + 1]) for i in range(nseg)]
    b = [0.5 * (blue[i] + blue[i + 1]) for i in range(nseg)]
    a = np.ones(nseg, np.float) * alpha
    lc = LineCollection(seg, colors=list(zip(r, g, b, a)), linewidth=2)
    ax.add_collection(lc)
def select_title():
    cur_dir_name = os.getcwd().split('/')[-1]
    if 'mp-' in cur_dir_name:
        try:
            formula = matproj.get_data(cur_dir_name, prop="pretty_formula")[0]["pretty_formula"]
            cur_dir_name = formula + '_' + cur_dir_name
        except:
            print('If the current folder name is only a mterials project id, the formula would be added to the figure title.')
    return cur_dir_name
def find_bs_labels_from_file(nself_dir = 'nself'):
    if not nself_dir.endswith('/'):
        nself_dir += '/'
    try:
        with open(nself_dir + 'KPOINTS', 'r') as kpts:
            counter = 0
            klist = []
            for l in kpts:
                counter += 1
                if counter > 4:
                    if counter in [5, 6]:
                        ordered = True
                    line = l.split()
                    if len(line) > 0:
                        if line[-1] in klist[-1:]:
                            ordered = True
                            continue
                        if ordered:
                            klist.append(line[-1])
                            ordered = False
                        else:
                            klist[-1] = klist[-1] + '|' + line[-1]
                            ordered = True

    except IOError:
        IOError('KPOINTS (line-mode) file must be present')
    labels = [r"$%s$" % lab for lab in klist]
    return labels
def find_e_range(bands, range_override = 10):
    emin = 1e100
    emax = -1e100
    for spin in bands.bands.keys():
        for b in range(bands.nb_bands):
            emin = min(emin, min(bands.bands[spin][b]))
            emax = max(emax, max(bands.bands[spin][b]))

    emin -= bands.efermi + 1
    emax -= bands.efermi - 1
    ax1.set_ylim(emin, emax)
    ax2.set_ylim(emin, emax)
    return max(emin, -range_override), min(emax, range_override)
if __name__ == "__main__":
    ### Check the input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-mpk", "--mpapikey",
                        help="Your Materials Project API key",
                        required=False, default='fDJKEZpxSyvsXdCt')
    parser.add_argument("-p", "--bs_projected_atom",
                        help="Projection of the atom's orbitals on the band structure e.g. default: -p O",
                        required=False, default = 'O')
    args = parser.parse_args()

    from pymatgen.matproj.rest import MPRester
    matproj = MPRester(args.mpapikey)
    # read data
    # ---------

    # kpoints labels
    # labels = [r"$L$", r"$\Gamma$", r"$X$", r"$U,K$", r"$\Gamma$"]
#    path = HighSymmKpath(mg.Structure.from_file("./nself/POSCAR")).kpath["path"]
#    labels = [r"$%s$" % lab for lab in path[0]]

    cur_dir_name = select_title()
    labels = find_bs_labels_from_file('nself')


    # density of states
    dosrun = Vasprun("./self/vasprun.xml")
    spd_dos = dosrun.complete_dos.get_spd_dos()

    # bands
    run = Vasprun("./nself/vasprun.xml", parse_projected_eigen=True)
    bands = run.get_band_structure("./nself/KPOINTS",
                                   line_mode=True,
                                   efermi=dosrun.efermi)

    # print(bands.__dict__)
    print(dir(bands))

    # set up matplotlib plot
    # ----------------------

    # general options for plot
    font = {'family': 'serif', 'size': 24}
    plt.rc('font', **font)

    # set up 2 graph with aspec ration 2/1
    # plot 1: bands diagram
    # plot 2: Density of States
    gs = GridSpec(1, 2, width_ratios=[2, 1])
    fig = plt.figure(figsize=(11.69, 8.27))
    fig.suptitle('Band Structure of ' + cur_dir_name)
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1])  # , sharey=ax1)

    # set ylim for the plot
    # ---------------------
    emin, emax = find_e_range(bands)


    # Band Diagram
    # ------------
    name = args.bs_projected_atom
    pbands = bands.get_projections_on_elts_and_orbitals({name: ["s", "p", "d"]})
    # pbands = bands.get_projection_on_elements
    # compute s, p, d normalized contributions
    contrib = np.zeros((bands.nb_bands, len(bands.kpoints), 3))
    for b in range(bands.nb_bands):
        for k in range(len(bands.kpoints)):
            sc = pbands[Spin.up][b][k][name]["s"]**2
            pc = pbands[Spin.up][b][k][name]["p"]**2
            dc = pbands[Spin.up][b][k][name]["d"]**2
            tot = sc + pc + dc
            if tot != 0.0:
                contrib[b, k, 0] = sc / tot
                contrib[b, k, 1] = pc / tot
                contrib[b, k, 2] = dc / tot

    # plot bands using rgb mapping
    for b in range(bands.nb_bands):
        rgbline(ax1,
                range(len(bands.kpoints)),
                [e - bands.efermi for e in bands.bands[Spin.up][b]],
                contrib[b, :, 0],
                contrib[b, :, 1],
                contrib[b, :, 2])

    # style
    ax1.set_xlabel("k-points")
    ax1.set_ylabel(r"$E - E_f$   /   eV")
    ax1.grid()

    # fermi level at 0
    ax1.hlines(y=0, xmin=0, xmax=len(bands.kpoints), color="k", lw=2)

    # labels
    nlabs = len(labels)
    step = len(bands.kpoints) / (nlabs - 1)
    for i, lab in enumerate(labels):
        ax1.vlines(i * step, emin, emax, "k")
    ax1.set_xticks([i * step for i in range(nlabs)])
    ax1.set_xticklabels(labels)

    ax1.set_xlim(0, len(bands.kpoints))
    ax1.set_ylim(emin, emax)
    #ax1.set_title("Bands diagram")

    # Density of states
    # -----------------

    ax2.set_yticklabels([])
    ax2.grid()
    ax2.set_xlim(1e-6, 3)
    ax2.set_xticklabels([])
    ax2.hlines(y=0, xmin=0, xmax=8, color="k", lw=2)
    ax2.set_xlabel("Density of States", labelpad=28)
    #ax2.set_title("Density of States")

    # spd contribution
    ax2.plot(spd_dos[OrbitalType.s].densities[Spin.up],
             dosrun.tdos.energies - dosrun.efermi,
             "r-", label="s", lw=2)
    ax2.plot(spd_dos[OrbitalType.p].densities[Spin.up],
             dosrun.tdos.energies - dosrun.efermi,
             "g-", label="p", lw=2)
    ax2.plot(spd_dos[OrbitalType.d].densities[Spin.up],
             dosrun.tdos.energies - dosrun.efermi,
             "b-", label="d", lw=2)

    # total dos
    ax2.fill_between(dosrun.tdos.densities[Spin.up],
                     0,
                     dosrun.tdos.energies - dosrun.efermi,
                     color=(0.7, 0.7, 0.7),
                     facecolor=(0.7, 0.7, 0.7))

    ax2.plot(dosrun.tdos.densities[Spin.up],
             dosrun.tdos.energies - dosrun.efermi,
             color=(0.3, 0.3, 0.3),
             label="total DOS")

    # plot format style
    # -----------------
    ax2.legend(fancybox=True, shadow=True, prop={'size': 18})
    ax2.set_ylim(emin, emax)

    plt.subplots_adjust(wspace=0)

    # plt.show()
    # plt.savefig(sys.argv[0].strip(".py") + ".pdf", format="pdf")
    plt.savefig(cur_dir_name + ".png", format="png")
