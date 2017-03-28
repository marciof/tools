Setup:

  $ . "$TESTDIR/setup.sh"
  $ echo "Bob" > file

Many plugin options (more than `ARRAY_INITIAL_CAPACITY`):

  $ show . -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1
  file

Order of argument processing:

  $ echo "Hello world!" | show -p dir=-1 . ./file
  Hello world!
  file
  Bob
