Setup:

  $ . $TESTDIR/setup.sh

Pass plugin option:

  $ show -p pipe:abc < /dev/null

Pass option to a disabled plugin:

  $ show -d pipe -p pipe:abc < /dev/null
  No such plugin or disabled.
  [1]

Pass option to a non-existent plugin:

  $ show -p p:abc
  No such plugin or disabled.
  [1]

Missing value for a plugin option:

  $ show -p p:
  No plugin option specified.
  [1]

Missing name for a plugin option:

  $ show -p :abc
  No plugin name specified.
  [1]
