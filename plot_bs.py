from pymatgen.io.vasp import Vasprun
from pymatgen.electronic_structure.plotter import BSPlotter, BSPlotterProjected

vr = Vasprun("nself/vasprun.xml")
bs = vr.get_band_structure(kpoints_filename="nself/KPOINTS", line_mode=True)
bsp = BSPlotter(bs)
#plt = bsp.get_elt_projected_plots(zero_to_efermi=False)
#plt.savefig("band_structure.png", format="png")
bsp.save_plot(filename="band_structure.png", img_format="png")
