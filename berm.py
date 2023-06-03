from pathlib import Path
import sys
import shutil
import time
import os
import sqlite3
from contextlib import closing
from subprocess import DEVNULL, Popen

BERM_DIR = Path('~/.local/share/berm').expanduser()
ARCHIVE_PATH = Path(BERM_DIR/'files.squashfs')
DATABASE_PATH = Path(BERM_DIR/'files.db')

class IntegrityChecks:
    def berm_dir_exists():
        # create berm dir if it doesnt exist
        if not Path.exists(BERM_DIR):
            print(f"No berm directory, creating one at {BERM_DIR}")
            Path.mkdir(BERM_DIR)

    def archive_exists():
        # create squashfs archive if it doesnt exist
        if not Path.exists(ARCHIVE_PATH):
            print(f"No archive, creating one at {ARCHIVE_PATH}")

            # create a temp file to put in archive (you need at least one to make one)
            with open(BERM_DIR/'init', "x") as temp:
                temp.write("12345")

            # mksquashfs ~/.local/share/berm/files/temp ~/.local/share/berm/files/files.squashfs
            new_archive_cmd = Popen([str(shutil.which("mksquashfs")), str(BERM_DIR/'init'), str(ARCHIVE_PATH)], stdout=DEVNULL)
            new_archive_cmd.wait()

            # remove temporary file
            os.remove(BERM_DIR/'init')

    def database_exists():
        if not Path.exists(DATABASE_PATH):
            print(f"No database, creating one at {DATABASE_PATH}")

            with closing(sqlite3.connect(DATABASE_PATH)) as con:
                cur = con.cursor()
                cur.execute("""CREATE TABLE operations (
                                path text,
                                time integer
                )""")
                con.commit()

    checks = (berm_dir_exists, archive_exists, database_exists)
    #BERM_DIR_CHECK = berm_dir_exists
    #STAGING_DIR_CHECK = staging_dir_exists
    #ARCHIVE_DIR_CHECK = archive_dir_exists
    #ARCHIVE_CHECK = archive_exists

def write_to_db(original_path: Path, time_of_operation: int):
    with closing(sqlite3.connect(DATABASE_PATH)) as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO operations VALUES ('{str(original_path)}', {time_of_operation})")
        con.commit()

def delete(file: Path):
    # save time of operation
    time_of_operation = round(time.time()*1000)

    # make folder for current operation
    operation_path = Path(BERM_DIR/str(time_of_operation))
    Path.mkdir(operation_path)
    shutil.move(file, operation_path)

    # append operation folder to archive
    archive_cmd = Popen([str(shutil.which("mksquashfs")), str(operation_path), str(ARCHIVE_PATH), "-keep-as-directory"], stdout=DEVNULL)
    archive_cmd.wait()

    # remove temp operation folder and write operation to db
    shutil.rmtree(operation_path)
    write_to_db(file.absolute(), time_of_operation)

def undo(time_of_operation: int):
    # get the path for this operation
    original_path = None
    with closing(sqlite3.connect(DATABASE_PATH)) as con:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM operations WHERE time={time_of_operation}")
        original_path = Path(cur.fetchone()[0])

    print("Unpacking archive...")
    unsquash_cmd = Popen([str(shutil.which("unsquashfs")), '-d', str(BERM_DIR/'unpacked'), str(ARCHIVE_PATH)], stdout=DEVNULL)
    unsquash_cmd.wait()

    print(f"Undoing operation on {original_path}...")
    shutil.move(BERM_DIR/'unpacked'/str(time_of_operation), os.getcwd())
    shutil.move(Path.cwd()/str(time_of_operation), Path.cwd()/'restored')

    print("Repacking archive...")
    os.remove(ARCHIVE_PATH)
    repack_files = [BERM_DIR/'unpacked'/name for name in os.listdir(BERM_DIR/'unpacked')]
    resquash_cmd = Popen([str(shutil.which("mksquashfs")), *repack_files, str(ARCHIVE_PATH), "-keep-as-directory"], stdout=DEVNULL)
    resquash_cmd.wait()
    shutil.rmtree(BERM_DIR/'unpacked')

    # delete entry
    with closing(sqlite3.connect(DATABASE_PATH)) as con:
        cur = con.cursor()
        cur.execute(f"DELETE FROM operations WHERE time={time_of_operation}")
        con.commit()
    print(f"{original_path} restored to {Path.cwd()/'restored'}")

if __name__ == "__main__":
    for check in IntegrityChecks.checks:
        check()
    print()

    delete(Path(sys.argv[1]))
    with closing(sqlite3.connect(DATABASE_PATH)) as con:
        cur = con.cursor()
        cur.execute("SELECT MAX(time) FROM operations")
        time_of_operation = cur.fetchone()[0]
        undo(time_of_operation)
