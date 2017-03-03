Setup:

  $ . $TESTDIR/setup.sh
  $ echo "Hello world!" > file

Display file:

  $ show file
  Hello world!

Display file from stdin:

  $ show < file
  Hello world!

Complain about file without permission to read:

  $ touch cant_read
  $ chmod u-r cant_read
  $ show cant_read
  file: cant_read: Permission denied
  [1]
  $ rm cant_read
