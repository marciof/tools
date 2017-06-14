Setup:

  $ . "$TESTDIR/setup.sh"

Complain about non-supported input:

  $ show doesnt_exist
  doesnt_exist: unsupported input
  [1]

Deactivate non-supported plugins automatically:

  $ PATH= show .
  .: unsupported input
  [1]

Do nothing without inputs and no available plugins:

  $ PATH= show
