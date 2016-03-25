Setup:

  $ . $TESTDIR/setup.sh

Pass plugin option:

  $ show -p pipe:abc < /dev/null

Pass option to a disabled plugin:

  $ show -x pipe -p pipe:abc < /dev/null
  No such plugin or disabled.

Pass option to a non-existent plugin:

  $ show -p p:abc
  No such plugin or disabled.

Missing value for a plugin option:

  $ show -p p:
  No plugin option specified.

Missing name for a plugin option:

  $ show -p :abc
  No plugin name specified.
