Setup:

  $ . "$TESTDIR/setup.sh"
  $ echo "foo" > file1
  $ echo "bar" > --file2
  $ ln -s file1 fileL
  $ touch cant_read
  $ chmod u-r cant_read

Display file:

  $ show file1
  foo

Display several files at once:

  $ show file1 ./--file2
  foo
  bar

Display file with leading dashes in its name:

  $ show -- --file2
  bar

Display NUL device:

  $ show /dev/null

Pipe output:

  $ show file1 | sed s/f/F/
  Foo

Display contents of link:

  $ show fileL
  foo

Display file without permission to read:

  $ show cant_read
  file: cant_read: Permission denied
  [1]
  $ chmod u+r cant_read

Teardown:

  $ chmod u+r cant_read
