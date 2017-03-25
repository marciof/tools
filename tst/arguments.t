Setup:

  $ . "$TESTDIR/setup.sh"
  $ echo "Bob" > file

Many plugin options:

  $ show.sh -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 -p dir=-1 .
  file

Order of argument processing:

  $ echo "Hello world!" | show.sh -p dir=-1 . ./file
  Hello world!
  file
  Bob
