Setup:

  $ . "$TESTDIR/setup.sh"
  $ mkdir -- dir1 --dir2
  $ touch -- dir1/file1 --dir2/file2

List current directory by default:

  $ show
  dir1
  --dir2

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
  dir1

List contents of link:

  $ ln -s dir1 dirL
  $ show dirL
  file1

List directory without permission to read:

  $ mkdir cant_read
  $ chmod u-r cant_read
  $ show cant_read
  ls: cannot open directory 'cant_read': Permission denied
  dir: cant_read: subprocess exited with an error code
  [1]
  $ chmod u+r cant_read
