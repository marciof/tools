Setup:

  $ . "$TESTDIR/setup.sh"
  $ echo Bob > file

Display piped input:

  $ echo "Hello world!" | show
  Hello world!

Display input file:

  $ show < file
  Bob

Don't display stdin when there are named inputs:

  $ echo Alice | show .
  file

Display input directory:

  $ show < .
  stdin: unable to read directory
  [1]

Display NUL device:

  $ show < /dev/null
