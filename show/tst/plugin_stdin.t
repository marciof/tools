Setup:

  $ . "$TESTDIR/setup.sh"
  $ echo Bob > file1

Display piped input:

  $ echo "Hello world!" | show
  Hello world!

Display slow piped input:

  $ (sleep 1 && echo foobar) | show
  foobar

Display input file:

  $ show < file1
  Bob

Display NUL device:

  $ show < /dev/null

Display input directory:

  $ show < .
  stdin: Is a directory
  [1]

Don't display stdin when there are named inputs:

  $ echo Alice | show .
  file1
