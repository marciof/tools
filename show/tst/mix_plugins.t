Setup:

  $ . "$TESTDIR/setup.sh"
  $ mkdir dir1
  $ echo Bob > file1
  $ echo John > dir1/file2

Mix plugins in the same call:

  $ show dir1 file1 . dir1/file2
  file2
  Bob
  dir1
  file1
  John
