Setup:

  $ . "$TESTDIR/setup.sh"
  $ mkdir dir
  $ echo "Bob" > dir/file

List directory:

  $ echo "Hello world!" | show -p dir=-1 dir dir/file
  Hello world!
  file
  Bob
