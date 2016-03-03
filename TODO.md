- http://rr-project.org
- https://github.com/andrewrk/malcheck
- https://matt.sh/howto-c
- Tests with coverage.
- Continuous integration.
- Plugin for `git show`.

Simplify code:
- Fix "ls" redirection to a plain text file, it's including color escapes.
- Remove the need for `Plugin_Result`
- Start with an empty list of `fds-in`.
  - Make the "pipe" plugin responsible for `stdin`.
  - Put directories from `stdin` into `args`.
- Do / While has `args`:
  - Run plugins (each consumes from `args` and puts into the fds-in list when appropriate).
  - Print all in the `fds-in` list.
  - If the nr of args hasn't changed, then no plugin handled and so exit loop.
  - This will preserve argument order when reading files and listing directories.
