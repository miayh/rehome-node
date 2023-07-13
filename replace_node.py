'''
TODO: create a new MO to replace an old one

1) Get MO's information (e.g. "..RRU-1..")
2) In simulated undo mode, delete MO
    a) Save command file as .mos
3) Replace all occurences of old name with new name (e.g. "..RRU-10..")
4) Run .mos that has the new name
'''

import amoshell
import sys
import subprocess as sb
import os

#def replace_node():

mo = amoshell.Amos()
rval, out, err = mo.moshell('WTC1EENB84', 'lt all; run getRadioInfo.mos')
if rval:
    print(err)

old_name = sys.argv[1]
new_name = sys.argv[2]
replace_cmd = "sed -i s/{}/{}/g example.mos".format(old_name, new_name)
os.system(replace_cmd)

rval, out, err = mo.moshell('WTC1EENB84', 'run radioCreation.mos; lt all')
#FieldReplaceableUnit=RU-100-8
if rval:
    print(err)



'''
if __name__ == '__main__':
    replace_node()
'''
