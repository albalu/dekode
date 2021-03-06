#!/usr/bin/env python
# This code extracts the phonon DOS information from DATA_all.txt and update the TCO MongoDB database
# Please contact alireza@wustl.edu if you had any questions. Bug reports are very much appreciated.
# By: Alireza Faghaninia

import pymongo

remote_port = 27018
db = pymongo.MongoClient("localhost", remote_port)["EM_Partita"]

core_per_node = 16
# at this point I'm assuming that the data is for n=1e20 and T=300K
counter = 0
with open('DATA_ALL.txt', 'r') as data:
	for line in data:
		counter += 1
		if counter > 1:
			(id, formula, sp_symbol, sp_number, sp_type, bgap, conductivity_n, conductivity_p, lo_phonon, static_dielectric, highf_dielectric, m_n, m_h, mobility_n, mobility_p, t_tot) = line.split()
				
			db.TCO_db.update({'mpid': id},{'$set': {'mpid': id, 'formula': formula, 'bgap': float(bgap), 'lo_phonon': float(lo_phonon), \
			'dielectric':{'static': float(static_dielectric), 'highf': float(highf_dielectric)}, 'n.mobility': float(mobility_n), \
			'n.conductivity': float(conductivity_n), 'n.effective_mass': float(m_n), 'p.mobility': float(mobility_p), \
			'p.conductivity': float(conductivity_p), 'p.effective_mass': float(m_h), 'cpuhr': float(t_tot)/3600*core_per_node, \
			'spacegroup.symbol': sp_symbol, 'spacegroup.number': sp_number, 'spacegroup.type': sp_type}},upsert = True)

#if I use this method the document in the database would be override!			'n': {'mobility': mobility_n, 'conductivity': conductivity_n, 'effective_mass': m_n}, 'p': {'mobility': mobility_p, 'conductivity': conductivity_p, 'effective_mass': m_h}, 'cpuhr': float(t_tot)/3600*core_per_node}},upsert = True)  # Actually this method "re-defines" n and p dictionary therefore removing thier other entries so the next line was used to explicitly update only specific entries

db.TCO_db.update({'mpid': id},{'$set': {'formula': formula, 'bgap': bgap, 'lo_phonon': lo_phonon, 'dielectric':{'static': static_dielectric, 'highf': highf_dielectric}, \
'n': {'mobility': mobility_n, 'conductivity': conductivity_n, 'effective_mass': m_n}, 'p': {'mobility': mobility_p, 'conductivity': conductivity_p, 'effective_mass': m_h}, 'cpuhr': float(t_tot)/3600*core_per_node}},upsert = True)
		
for d in db.TCO_db.find():
#	if d.get('n'):
#		print d['n']['conductivity']
	print d['formula']

