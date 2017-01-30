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

id_list = ["m-4884", "m-3135", "m-1011"]

for id in id_list:
    comp = db.materials.find_one({"material_id": id})
    folder_name = comp["formula_pretty"].replace("(", "_")
    folder_name = folder_name.replace(")", "_")

    if os.path.exists(folder_name):
        print("The folder {} already exists".format(folder_name))
        continue
    else:
        os.system("cp -r initial " + folder_name)
        os.chdir(folder_name)

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
    os.system("qsub partita.sh")
    os.chdir("../")
