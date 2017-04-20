Setup:

  $ . "$TESTDIR/setup.sh"
  $ touch file1

Pass plugin option:

  $ show -p dir=-1
  file1

Pass option to a disabled plugin:

  $ show -d dir -p dir=-1 < /dev/null

Pass option to a non-existent plugin:

  $ show -p doesnt_exist=abc
  doesnt_exist=abc: no such plugin
  [1]

Missing value for a plugin option:

  $ show -p dir=
  dir=: no plugin option specified
  [1]

Missing name for a plugin option:

  $ show -p =-1
  =-1: no plugin name specified
  [1]

Many plugin options (more than `ARRAY_INITIAL_CAPACITY`):

  $ show -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1
  file1
