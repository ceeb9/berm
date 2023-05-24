import sys
import os
import shutil
import time
import lzma
from dataclasses import dataclass
from typing import Callable

# 1. assess file type, create new folder and archive if doesnt exist
# 2. decompress that file type's archive
# 3. move file to the deleted files folder of that type, 
#    renamed as the time it moved in unix millis
# 4. recompress everything in that folder

# maps each flag to the corresponding:
# 1: expected length
# 2: function
# 3: flag for that function
@dataclass
class Mode:
    operation: Callable
    operation_flag: str
    expected_len: int

def trash(mode, filename):
    print("trash", mode, filename)

    # check if the file specified is valid for the current mode
    if mode == "FILE":
        if os.path.isdir(f"{CWD}/{filename}"):
            print("use -r to trash directories")
            sys.exit()
        elif not os.path.isfile(f"{CWD}/{filename}"):
            print("file not found")
            sys.exit()
    elif mode == "DIR":
        if os.path.isfile(f"{CWD}/{filename}"):
            print("remove the -r flag for files")
            sys.exit()
        elif not os.path.isdir(f"{CWD}/{filename}"):
            print("directory not found")
            sys.exit()

    new_filename = round(time.time()*1000)
    old_file_path = f"{CWD}/{filename}"

    # 128mb chunks
    chunk_size = 134217728
    lzc = lzma.LZMACompressor()
    
    # read chunks of file in and write them as compressed
    with open(old_file_path, "rb") as original:
        with lzma.open(f"{BERM_PATH}/files/{new_filename}", "w") as new:
            while True:
                data = original.read(chunk_size)
                new.write(data) # write compressed

                print("size", sys.getsizeof(data))

                if sys.getsizeof(data) < chunk_size:
                    break

    write_to_db(new_filename, mode[0], f"{CWD}/{filename}", f"{BERM_PATH}/files/{new_filename}")
    return

def undo(mode, filename=""):
    print("undo", mode, filename)
    if mode == "LAST":
        print("undo not implemented")
    elif mode == "FILE":
        print("undo not implemented")
    elif mode == "DIR":
        print("undo not implemented")
    return

def search(mode, filename):
    print("search", mode, filename)
    if mode == "ALL":
        print()
    elif mode == "HERE":
        print()
    return

MODES = {
        "-r": Mode(trash, "DIR", 2),

        "-u": Mode(undo, "LAST", 1),
        "-uf": Mode(undo, "FILE", 2),
        "-ur": Mode(undo, "DIR", 2),

        "-s": Mode(search, "ALL", 2),
        "-sh": Mode(search, "HERE", 2),
        }

HELP_MSG = """
           pass a file with no arguments to send that file to trash.

           -r <directory>:      trash a directory

            undo operations will restore the file/directory to the original directory of the file
            if not possible, they will then restore the file/directory to the current directory
        
           -u:                  undo the last operation
           -uf <file>:          undo an operation that was done on a file
           -ur <directory>:     undo an operation that was done on a directory

           -s <name>:           search for a trashed file or directory
           -sh <name>:          search for a trashed file or directory that was deleted in this directory
           """

BERM_PATH = os.path.expanduser("~/.local/share/berm")
CWD = os.getcwd()

def database_exists() -> bool:
    if os.path.exists(BERM_PATH) and os.path.isfile(f"{BERM_PATH}/db") and os.path.exists(f"{BERM_PATH}/files"):
        print("db exists")
        return True
    else:
        print("no db")
        return False

def create_database():
    print("creating database")
    # create the main directory, file directory, and database file
    if not os.path.exists(BERM_PATH):
        os.mkdir(BERM_PATH)
    if not os.path.exists(f"{BERM_PATH}/files"):
        os.mkdir(f"{BERM_PATH}/files")
    if not os.path.isfile(f"{BERM_PATH}/db"):
        open(f"{BERM_PATH}/db", "x")
    return

# time: unix millis
# filetype: F or D for file or directory
# orig_path: the path of the file before it was trashed
# dest_path: the path of the file now (after trashing)
def write_to_db(time: int, filetype: str, orig_path: str, dest_path: str):
    with open(f"{BERM_PATH}/db", "a") as db:
        entry = f"{time},{filetype},{orig_path},{dest_path}\n"
        db.write(entry)
        print(entry)
    return

def parse_arguments(argv):
    # check if nothing was passed
    if len(argv) == 0:
        print(HELP_MSG)
        sys.exit()

    # check if a valid flag was passed
    elif argv[0] not in MODES.keys():
        # if they were trying to pass a flag, show help
        if argv[0][0] == "-":
            print(HELP_MSG)
            sys.exit()
        else:
            # otherwise, trash the file specified
            trash("FILE", argv[0])

    # check if the length of args is what we expected
    elif len(argv) != MODES[argv[0]].expected_len:
        print(HELP_MSG)
        sys.exit()
    else:
        current_mode = MODES[argv[0]]
        current_mode.operation(current_mode.operation_flag, *argv[1:])

def main(argv):
    if not database_exists():
        create_database()
    parse_arguments(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
