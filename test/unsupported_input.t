Setup:

  $ . $TESTDIR/setup.sh

Complain about non-supported input:

  $ show -d file -d ls -d pager -d pipe doesnt_exist
  Unsupported input: doesnt_exist
  [1]
