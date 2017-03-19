Setup:

  $ . $TESTDIR/setup.sh

Help screen:

  $ show -h
  Usage: show [OPTION]... [INPUT]...
  Version: \d+(\.\d+)(\.\d+) (re)
   (esc)
  Options:
    -h           display this help and exit
    -d NAME      disable a plugin
    -p NAME=OPT  pass an option to a plugin
   (esc)
  Plugins:
    stdin        read standard input
    file         read files
    dir          list directories via `ls`
    vcs          show VCS revisions via `git`
    pager        page output via `less` when needed
