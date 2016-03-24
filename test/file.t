Setup:

  $ . $TESTDIR/setup.sh
  $ echo "Hello world!" > file

Display file:

  $ show file
  Hello world!

Display file from stdin:

  $ show < file
  Hello world!
