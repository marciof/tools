Setup:

  $ . "$TESTDIR/setup.sh"

Help screen:

  $ show -h
  Usage: show [OPTION]... [INPUT]...
  Version: 0.12.0
   (esc)
  Options:
    -h           display this help and exit
    -d NAME      disable a plugin
    -p NAME=OPT  pass an option to a plugin
   (esc)
  Plugins:
    stdin        read standard input, by default
    file         read files
    dir          list directories via `ls`, cwd by default
    vcs          show VCS revisions via `git`
    pager        page output via `less`, when needed

Show unavailable plugins in the help screen:

  $ PATH= show -h
  Usage: show [OPTION]... [INPUT]...
  Version: 0.12.0
   (esc)
  Options:
    -h           display this help and exit
    -d NAME      disable a plugin
    -p NAME=OPT  pass an option to a plugin
   (esc)
  Plugins:
    stdin        read standard input, by default
    file         read files
  x dir          list directories via `ls`, cwd by default
  x vcs          show VCS revisions via `git`
  x pager        page output via `less`, when needed
