from pathlib import Path
import sys
import shutil
import time
import os
from subprocess import DEVNULL, PIPE, STDOUT, Popen

BERM_DIR = Path('~/.local/share/berm').expanduser()
STAGING_DIR = Path(BERM_DIR/'staging')
ARCHIVE_DIR = Path(BERM_DIR/'files')
ARCHIVE_PATH = Path(ARCHIVE_DIR/'files.squashfs')

class IntegrityChecks:
    def berm_dir_exists():
        # create berm dir if it doesnt exist
        if not Path.exists(BERM_DIR):
            print(f"No berm directory, creating one at {BERM_DIR}")
            Path.mkdir(BERM_DIR)

    def staging_dir_exists():
        # create staging dir if it doesnt exist
        if not Path.exists(STAGING_DIR):
            print(f"No staging directory, creating one at {STAGING_DIR}")
            Path.mkdir(STAGING_DIR)

    def archive_dir_exists():
        # create squashfs archive dir if it doesnt exist
        if not Path.exists(ARCHIVE_DIR):
            print(f"No archive directory, creating one at {ARCHIVE_DIR}")
            Path.mkdir(ARCHIVE_DIR)

    def archive_exists():
        # create squashfs archive if it doesnt exist
        if not Path.exists(ARCHIVE_PATH):
            print(f"No archive, creating one at {ARCHIVE_PATH}")

            # create a temp file to put in archive (you need at least one to make one)
            with open(ARCHIVE_DIR/'init', "x") as temp:
                temp.write("12345")

            # mksquashfs ~/.local/share/berm/files/temp ~/.local/share/berm/files/files.squashfs
            new_archive_cmd = Popen([str(shutil.which("mksquashfs")), str(ARCHIVE_DIR/'temp'), str(ARCHIVE_PATH)], stdout=DEVNULL)
            new_archive_cmd.wait()

            # remove temporary file
            os.remove(ARCHIVE_DIR/'init')

    checks = (berm_dir_exists, staging_dir_exists, archive_dir_exists, archive_exists)
    #BERM_DIR_CHECK = berm_dir_exists
    #STAGING_DIR_CHECK = staging_dir_exists
    #ARCHIVE_DIR_CHECK = archive_dir_exists
    #ARCHIVE_CHECK = archive_exists

def delete(file: Path):
    # save time of operation
    time_of_operation = round(time.time()*1000)

    # make folder for current operation
    operation_path = Path(STAGING_DIR/str(time_of_operation))
    Path.mkdir(operation_path)
    shutil.move(file, operation_path)

    # append operation folder to archive
    archive_cmd = Popen([str(shutil.which("mksquashfs")), str(operation_path), str(ARCHIVE_PATH), "-keep-as-directory"], stdout=DEVNULL)
    archive_cmd.wait()

    # delete operation folder
    shutil.rmtree(operation_path)

if __name__ == "__main__":
    for check in IntegrityChecks.checks:
        check()
    delete(Path(sys.argv[1]))
