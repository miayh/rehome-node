"""
Author: Mia Yamada-Heidner
Date: 08/11/2023

Creates MOs of an existing node to be used if/when rehoming a node.
"""

import amoshell
import sys
import os
import argparse
import multiprocessing as mp
import functools
import time
import re

OG_MOS_CREATION_FILES = []

def check_status(rval, err):
    """Checks the return value, printing the error and exiting if it is 1.

    Args:
    - rval: The return value
    - err: The error produced
    """
    if rval:
        print(err)
        sys.exit(1)

def setup_parser():
    """Creates and returns a new parser to parse the command line arguments.
    
    Returns:
    - The parser created
    """
    parser = argparse.ArgumentParser(description='Extracts info from a node' \
                                     ' to be recreated in another.')
    parser.add_argument('srcnode',
                        help='The name of the node from which to copy information')
    parser.add_argument('destnode',
                        help='The name of the node into which information will be transformed')
    parser.add_argument('dir', help='The desired name of the directory that will' \
                        ' store the MO creation files')
    parser.add_argument('-s', '--srcname', help='The current name of the MO' \
                        ' off of which to base the new MO (e.g. "RRU-1")')
    parser.add_argument('-n', '--newname', help='The desired name for the new MO (e.g. "RRU-100")')
    return parser

def create_mos_files(amos, node):
    """Creates .mos files from an existing node and lists the names of all the files created
    in a separate file named "mos_filenames.txt".

    Args:
    - amos: The object to use to execute moshell commands on the node
    - node: The name of the node from which to copy information
    
    Throws: 
    - IOError, if there is an issue reading the newly-created file "mos_filenames.txt"
    """
    print("Creating .mos files...")
    rval, out, err = amos.moshell(node, "lt all; run collectNodeInfo.mos cmds.mos")
    check_status(rval=rval, err=err)
    mos_files_cmd = "ls | grep -E '^(radio|rilink|antenna|sector|carrier|cell)Creation.mos'" \
                    " > mos_filenames.txt"
    os.system(mos_files_cmd)
    try:
        with open('./mos_filenames.txt', 'r') as file:
            for line in file:
                mos_file = line.strip()
                OG_MOS_CREATION_FILES.append(mos_file)
    except IOError:
        print("Error reading the file.")
    
def search_in_file(file_path, str):
    """Searches for a specific substring in the given file path.
    
    Args:
    - file_path: The file path where the document in which to search is
    - str: The string to look for

    Returns:
    - True if the string can be found, false otherwise

    Throws: 
    - IOError, if there is an issue reading the given file
    """
    try:
        with open(file_path, 'r') as file:
            contents = file.read()
            if str in contents:
                return True
    except IOError:
        print("Error reading the file.")
    return False

def create_new_mo(amos, src_node, dest_node, mos_file, src_name, new_name):
    """Creates a new version of the .mos creation file (based off of the original)
       where `src_name` is replaced with `new_name`.

    Args:
    - amos: The object to use to execute moshell commands on the node
    - src_node: The name of the node from which to copy information
    - dest_node: The name of the node into which information will be transformed
    - mos_file: The file with the necessary commands to create the MO
    - src_name: The name of a current MO (e.g. "RU-1") off of which to base the new MO
    - new_name: The new name for the MO (e.g. "RU-100")
    """
    new_mo_file = "new_{}".format(mos_file)
    print("Creating {}".format(new_mo_file))
    make_new_cmd = "touch {} && cp {} {}".format(new_mo_file, mos_file, new_mo_file)
    os.system(make_new_cmd)
    replace_cmd = "sed -i s/{}/{}/g {}".format(src_node, dest_node, new_mo_file)
    os.system(replace_cmd)
    replace_cmd = "sed -i s/{}/{}/g {}".format(src_name, new_name, new_mo_file)
    print("Modifying {}...".format(new_mo_file))
    os.system(replace_cmd)
    create_cmd = "run {}; lt all".format(new_mo_file)
    unit = mos_file[:-12]
    print("Creating the new {}".format(unit))
    rval, out, err = amos.moshell(dest_node, create_cmd)
    check_status(rval=rval, err=err)

def create_existing_mos(amos, src_node, dest_node, mos_file):
    """Creates the existing MOs in one node to be added to another node.

    Args:
    - amos: The object to use to execute moshell commands on the node
    - src_node: The name of the node from which to copy information
    - dest_node: The name of the node into which information will be transformed
    - mos_file: The file with the necessary commands to create the MO
    """
    replace_cmd = "sed -i s/{}/{}/g {}".format(src_node, dest_node, mos_file)
    os.system(replace_cmd)
    create_cmd = "run {}; lt all".format(mos_file)
    unit = mos_file[:-12]
    print("Creating the existing MOs related to the {}...".format(unit))
    rval, out, err = amos.moshell(dest_node, create_cmd)
    check_status(rval=rval, err=err)

def transfer_files(dir):
    """Transfers the relevant MO files into a new directory.

    Args:
    - dir: The directory where the files will be moved
    """
    new_dir_cmd = "mkdir {}".format(dir)
    print("Moving the created files into the new" \
          " directory '{}'...".format(dir))
    os.system(new_dir_cmd)
    move_cmd = "mv {} {}/".format("mos_filenames.txt", dir)
    os.system(move_cmd)
    move_cmd = "ls" \
               " | grep -E '^(new_)*(radio|rilink|antenna|sector|carrier|cell)(Creation|Properties).(txt|mos)'" \
               " | xargs -d\"\n\" mv -t {}/".format(dir)
    os.system(move_cmd)

def create_mos(amos, src_node, dest_node, src_name, new_name, mos_file):
    """
    Creates all existing and new (if applicable) MOs in a node.
 
    Args:
    - amos: The object to use to execute moshell commands on the node
    - src_node: The name of the node from which to copy information
    - dest_node: The name of the node into which information will be transformed
    - src_name: The current name of an MO (e.g. "RRU-1")
    - new_name: The desired name for the MO in the node (e.g. "RRU-100")
    - mos_file: The file with the necessary commands to create the MO
    """
    if src_name and new_name:
        found = search_in_file(mos_file, src_name)
        if found:
            create_new_mo(amos, src_node, dest_node, mos_file, src_name, new_name)
    create_existing_mos(amos, src_node, dest_node, mos_file)

def recreate_node(src_node, dest_node, dir, src_name, new_name):
    """If `src_name` and `new_name` are specified, recreates a node but
      replaces instances of an MO named `src_name` with `new_name` in the other node.
      Otherwise, recreates a node as is and transfers the information to another node.

    Args:
    - src_node: The name of the node from which to copy information
    - dest_node: The name of the node into which information will be transformed
    - dir: The name of the new directory which will store all the .mos and .txt files
           based on the source node after the function is called
    - src_name: The current name of an MO (e.g. "RRU-1")
    - new_name: The desired name for the MO in the node (e.g. "RRU-100")
    """
    amos = amoshell.Amos()
    create_mos_files(amos, src_node)
    num_processes = mp.cpu_count()
    pool = mp.Pool(num_processes)
    func_with_args = functools.partial(create_mos, amos,
                                        src_node, dest_node,
                                        src_name, new_name)
    pool.map(func_with_args, OG_MOS_CREATION_FILES)
    transfer_files(dir)

def main():
    """
    Example usages:
    python recreate_node.py WTC1EENB100 WTC1EENB101 WTC1EENB101
    python recreate_node.py WTC1EENB101 WTC1EENB101 WTC1EENB101 -s RU-1 -n RU-100
    """
    start = time.time()
    parser = setup_parser()
    args = parser.parse_args()
    src_node = args.srcnode
    dest_node = args.destnode
    dir = args.dir
    src_name = args.srcname
    new_name = args.newname
    
    if (src_name and not new_name) or (not src_name and new_name):
        parser.error("Both -o/--oldname and -n/--newname are required.")
    
    if src_name and new_name:
        recreate_node(src_node, dest_node, dir, src_name, new_name)
    else:
        recreate_node(src_node, dest_node, dir, None, None)

    end = time.time()
    elapsed_time = end - start
    print("Finished!")
    print("Elapsed time: {:.3f}s".format(elapsed_time))

if __name__ == '__main__':
    main()
