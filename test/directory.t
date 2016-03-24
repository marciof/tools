Setup:

  $ . $TESTDIR/setup.sh
  $ mkdir dir
  $ touch dir/file

List directory:

  $ show dir
  file

List directory from stdin:

  $ show < dir
  file
