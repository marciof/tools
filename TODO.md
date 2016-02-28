- https://github.com/andrewrk/malcheck
- https://matt.sh/howto-c
- Tests with coverage.
- Continuous integration.
- Allow iterating using only callbacks to avoid allocating memory and to be faster?
- Plugin for `git show`.
- Put directories from `stdin` into `args`.
- Preserve arguments order when reading files and listing directories.
- Make the "pipe" plugin responsible for `stdin`.
- Allow inserting and removing list elements while iterating.

Simplify code:
- Start with an empty list of fds-in.
- Do / While has `args`:
  - Run plugins (each consumes from `args` and puts into the fds-in list when appropriate).
  - Print all in the fds-in list.
  - If the nr of args hasn't changed, then no plugin handled and so exit loop.
