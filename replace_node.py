'''
Author: Mia Yamada-Heidner
Date: 07/17/2023

Creates a new MO based on an existing one.
New node to be used if/when rehoming a node. 
'''

import amoshell
import sys
import os

def check_status(rval, err):
    if rval:
        print(err)
        sys.exit(1)

def create_radio():
    mo = amoshell.Amos()
    # generate a .mos file to create the new MO
    rval, out, err = mo.moshell('WTC1EENB84', 'lt all; run getRadioInfo.mos radioInfo.txt radioCreation.mos')
    check_status(rval=rval, err=err)
    
    # replace all occurences of given old name with given new name 
    # e.g. "RRU-1" to be replaced with "RRU-10"
    old_name = sys.argv[1]
    new_name = sys.argv[2]
    replace_cmd = "sed -i s/{}/{}/g radioCreation.mos".format(old_name, new_name)
    os.system(replace_cmd)
    
    # create new MO
    rval, out, err = mo.moshell('WTC1EENB84', 'run radioCreation.mos; lt all')
    check_status(rval=rval, err=err)

if __name__ == '__main__':
    create_radio()
