"""
Author: Mia Yamada-Heidner
Date: 07/24/2023

Creates differently named MOs that make up an existing node.
New MO creation files may be used if/when rehoming a node.
"""

import amoshell
import sys
import os

def check_status(rval, err):
    """Checks the return value, printing the error and exiting if it is 1.

    Args:
    - rval: The return value
    - err: The error produced
    """
    if rval:
        print(err)
        sys.exit(1)

def recreate_node(node, old_name, new_name, dir):
    """Recreates a node but replaces instances of `old_name` with `new_name` in the new node.

    Args:
    - node: The name of the node from which to copy information
    - old_name: The current name of MO(s) to be changed in the new version of the node (e.g. "RRU-1")
    - new_name: The desired name for the MO(s) in the new version of the node (e.g. "RRU-100")
    - dir: The name of the new directory which will store all the .mos and .txt files
           with pertinent information about the node after the function is called
    """
    mo = amoshell.Amos()
    # generate a .mos file to create the new MO
    print("Creating .mos files...")
    rval, out, err = mo.moshell(node, "lt all; run collectNodeInfo.mos cmds.mos")
    check_status(rval=rval, err=err)
    mos_files_cmd = "ls | grep -E '^(radio|rilink|antenna|sector|carrier|cell)Creation.mos' > mos_filenames.txt"
    os.system(mos_files_cmd)
    new_dir_cmd = "mkdir {}".format(dir)
    os.system(new_dir_cmd)
    try:
        with open('./mos_filenames.txt', 'r') as file:
            for line in file:
                mos_file = line.strip()
                # find instances of the old name in the .mos files
                # and modify them to be the new name
                replace_cmd = "sed -i s/{}/{}/g {}".format(old_name, new_name, mos_file)
                print("Modifying {}...".format(mos_file))
                os.system(replace_cmd)
                create_cmd = "run {}; lt all".format(mos_file)
                print("Creating the new MOs...")
                rval, out, err = mo.moshell(node, create_cmd)
                check_status(rval=rval, err=err)
        move_cmd = "mv {} {}/".format("mos_filenames.txt", dir)
        os.system(move_cmd)
        move_cmd = "ls | grep -E '^(radio|rilink|antenna|sector|carrier|cell)(Info|Creation|Properties).(txt|mos)' | xargs -d\"\n\" mv -t {}/".format(dir)
        os.system(move_cmd)
    except IOError:
        print("Error reading the file.")

if __name__ == '__main__':
    # E.g.:
    # python recreate_node.py WTC1EENB101 RU-8 RU-800 WTC1EENB101
    node = sys.argv[1]       # WTC1EENB101
    old_name = sys.argv[2]   # RU-8
    new_name = sys.argv[3]   # RU-800
    dir = sys.argv[4]        # WTC1EENB101
    recreate_node(node, old_name, new_name, dir)
    print("Finished!")
