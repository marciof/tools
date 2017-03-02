Setup:

  $ . $TESTDIR/setup.sh
  $ mkdir -- dir1 --dir2
  $ touch -- dir1/file1 --dir2/file2

List directory:

  $ show dir1
  file1

List directory with leading dashes in its name:

  $ show -- --dir2
  file2

List directory from stdin:

  $ show < dir1
  file1

List directory with a custom option:

  $ show -p dir=-a dir1
  .
  ..
  file1
