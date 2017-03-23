Setup:

  $ . "$TESTDIR/setup.sh"

Complain about non-supported input:

  $ show doesnt_exist
  doesnt_exist: Unsupported input
  [1]

Deactivate non-supported plugin automatically:

  $ PATH=/bin VALGRIND_LEAK_CHECK= show @
  @: Unsupported input
  [1]
