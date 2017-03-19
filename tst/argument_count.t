Setup:

  $ . "$TESTDIR/setup.sh"
  $ touch file

Many plugin options (more than `ARRAY_INITIAL_CAPACITY`):

  $ show . -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1
  file
