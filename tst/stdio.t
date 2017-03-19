Setup:

  $ . "$TESTDIR/setup.sh"

Display piped input:

  $ echo "Hello world!" | show
  Hello world!

Discard output:

  $ show > /dev/null
