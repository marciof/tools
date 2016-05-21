Setup:

  $ . $TESTDIR/setup.sh

Complain about non-supported input:

  $ show -d file -d ls -d less -d pipe doesnt_exist
  Unsupported input: doesnt_exist
  [1]
