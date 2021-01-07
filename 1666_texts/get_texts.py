#! /usr/bin/env python3

import subprocess

with open('texts.csv', 'r') as textlist:
	list_of_ids = textlist.read().split('\n')

print(list_of_ids)

for i in list_of_ids[:-1]:
	small_i = i[:3]
	print(small_i)
	location = "/home/data/phase1texts/texts/{}/{}.xml".format(small_i,i)
	print(location)
	command = "cp {} .".format(location)
	try:
		subprocess.call(command, shell=True)
	except:
		pass
