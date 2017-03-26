Setup:

  $ . "$TESTDIR/setup.sh"

Complain about non-supported input:

  $ show doesnt_exist
  doesnt_exist: unsupported input
  [1]

Deactivate non-supported plugin automatically:

  $ PATH=/bin show @
  @: unsupported input
  [1]
