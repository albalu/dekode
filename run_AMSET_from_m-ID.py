import json
import os

import gridfs
import zlib

from pymatgen.io.vasp import BandStructure, BandStructureSymmLine
from pymatgen import Structure
from pymatgen.symmetry.bandstructure import HighSymmKpath
from pymatgen.io.vasp import Kpoints
from pymongo import MongoClient

db = MongoClient(host="localhost", port=57017)["aj_thermoelectrics"]
print db.authenticate("CaptAmerica", "VibraniumSteel")

id_list = ["m-529"]

for id in id_list:
    comp = db.materials.find_one({"material_id": id})
    if os.path.exists(comp["formula_pretty"]):
        print("The folder {} already exists".format(comp["formula_pretty"]))
        continue
    else:
        os.system("cp -r initial " + comp["formula_pretty"])
        os.chdir(comp["formula_pretty"])

    st = comp["structure"]
    s = Structure.from_dict(st)
    s.to(filename="POSCAR")
    ibz = HighSymmKpath(s)

    kpoints = list()
    labels = list()
    for path in ibz.kpath["path"]:
        for kpts in path:
            kpoints.append(ibz.kpath["kpoints"][kpts])
            labels.append(kpts)

    Kpoints(comment = "Line mode for {} {} {}".format(comp["formula_pretty"], "sg" + str(comp["spacegroup"]["number"]), comp["spacegroup"]["symbol"]),
            num_kpts = 20,
            style = Kpoints.supported_modes.Line_mode,
            coord_type = "Reciprocal",
            kpts = kpoints,
            labels = labels,
            ).write_file("KPOINTS_NSELF")
#    os.system("qsub partita.sh")
    os.chdir("../")
