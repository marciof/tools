Setup:

  $ . "$TESTDIR/setup.sh"

Pass plugin option:

  $ show -p stdin=abc < /dev/null

Pass option to a disabled plugin:

  $ show -d stdin -p stdin=abc < /dev/null
  Invalid options: No such plugin or disabled
  [1]

Pass option to a non-existent plugin:

  $ show -p p=abc
  Invalid options: No such plugin or disabled
  [1]

Missing value for a plugin option:

  $ show -p p=
  Invalid options: No plugin option specified
  [1]

Missing name for a plugin option:

  $ show -p =abc
  Invalid options: No plugin name specified
  [1]
