Setup:

  $ . "$TESTDIR/setup.sh"
  $ mkdir dir
  $ echo Bob > file1
  $ echo John > dir/file2

Mix plugins in the same call:

  $ show dir file1 . dir/file2
  file2
  Bob
  dir
  file1
  John
