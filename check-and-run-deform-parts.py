#!/usr/bin/env python
# This code will make sure that all titles either Title, title, OPTtitle or OPTTitle in .bib files
# are in {{ }} so that the capitalazation of the words and chemical compositions are correct in styles such as unsrt
# Please contact alireza@wustl.edu if you had any questions. Bug reports are very much appreciated.
# By: Alireza Faghaninia

import argparse
import os

if __name__ == "__main__":
### Check the input arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("-n","--name", help="The name of the main folder to be checked", required = False, default = 'part')
	args = parser.parse_args()

	submit_command = 'qsub '
	vasp_script = 'vasp-ib2.csh'
	
	for i in ['-5', '-4', '-3', '-2', '-1', '0', '1', '2', '3', '4', '5']:
		if os.path.exists(args.name + i):
			os.chdir(args.name + i)
			if 'Voluntary context switches:' in open('OUTCAR').read():
				print('%s %s\n' %('done:', args.name + i))
			else:
				print('%s %s\n' %('INCOMPLETE:', args.name + i))
				os.system('rm log*')
				os.system(submit_command + vasp_script)
			os.chdir('../')
		else:
			print('%s %s\n' % ('No',args.name + i + '/'))
