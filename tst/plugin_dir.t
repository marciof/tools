Setup:

  $ . "$TESTDIR/setup.sh"
  $ mkdir -- dir1 --dir2
  $ touch -- dir1/file1 --dir2/file2
  $ ln -s dir1 dirL
  $ mkdir cant_read
  $ chmod u-r cant_read

List current directory by default:

  $ show
  cant_read
  dir1
  --dir2
  dirL

List directory:

  $ show dir1
  file1

List several directories at once:

  $ show dir1 ./--dir2
  file1
  file2

List directory with a custom option:

  $ show -p dir=-a dir1
  .
  ..
  file1

List directory with leading dashes in its name:

  $ show -- --dir2
  file2

Pipe output:

  $ show . | head -n1
  cant_read

List contents of link:

  $ show dirL
  file1

List directory without permission to read:

  $ show cant_read
  ls: cannot open directory 'cant_read': Permission denied
  dir: cant_read: subprocess exited with an error code
  [1]

Teardown:

  $ chmod u+r cant_read
