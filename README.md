# berm
better rm, a small file deletion utility that uses squashfs to store deleted files
- delete files with compression
- undo deletions

## file deletion component
1. user deletes file
2. file is moved to staging area
3. move file into folder named the original operation time in unix millis
4. add folder to squashfs archive
5. delete item from staging area
6. entry added to db:
    name
    original filepath
    time of operation as written in queue db

## undo component
1. search database for unix timestamp of operation to undo
2. unsquash filesystem
3. move contents of squashfs-root/(timestamp)/ to specified restore directory, cwd if none specified
4. delete squashfs-root/(timestamp)
5. resquash squashfs-root
6. delete unsquashed filesystem
7. remove entry from db
