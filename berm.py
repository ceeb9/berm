import sys
import os
from dataclasses import dataclass
from typing import Callable

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
    return

def undo(mode, filename=""):
    print("undo", mode, filename)
    return

def search(mode, filename):
    print("search", mode, filename)
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

           -u:                  undo the last operation
           -uf <file>:          undo an operation that was done on a file
           -ur <directory>:     undo an operation that was done on a directory

           -s <name>:           search for a trashed file or directory
           -sh <name>:          search for a trashed file or directory that was deleted in this directory
           """

DATABASE_PATH = "~/.local/share/berm"

def database_exists() -> bool:
    if os.path.isfile(f"{os.path.expanduser(DATABASE_PATH)}/db"):
        print("db exists")
        return True
    else:
        print("no db")
        return False

def create_database():
    print("create database")
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

    # if none of the above, we can execute as normal
    else:
        current_mode = MODES[argv[0]]
        current_mode.operation(current_mode.operation_flag, *argv[1:])

def main(argv):
    if not database_exists():
        create_database()
    parse_arguments(argv)

if __name__ == "__main__":
    main(sys.argv[1:])
