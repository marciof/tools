Setup:

  $ . "$TESTDIR/setup.sh"
  $ echo Bob > file

Display piped input:

  $ echo "Hello world!" | show
  Hello world!

Display slow piped input:

  $ (sleep 1 && echo foobar) | show
  foobar

Display input file:

  $ show < file
  Bob

Display NUL device:

  $ show < /dev/null

Display input directory:

  $ show < .
  stdin: unable to read directory
  [1]

Don't display stdin when there are named inputs:

  $ echo Alice | show .
  file
