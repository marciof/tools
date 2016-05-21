This project adheres to [Semantic Versioning](http://semver.org).

# Dependencies #

See `.travis.yml` for details.

# To Do #

- Use simple C strings to avoid storing buffer lengths separately?
- Reduce memory allocation.
- Profile each change.
  - http://geoff.greer.fm/ag/speed/
  - `./bin/callgrind -p pager:-E -p pager:+$(wc -l < /var/log/syslog.1) /var/log/syslog.1`
- Lint and static analysis?
  - http://clang-analyzer.llvm.org
- Tests with coverage.
  - https://github.com/andrewrk/malcheck
  - https://github.com/google/sanitizers
- Character counting for the pager plugin actually counts bytes, not logical characters.
- Allow line numbers in input names to scroll to when paging.
- Change array type to allow any element size? Will avoid many memory allocations, but will increase copying.
- Improve error messages to give more context (which plugin, etc).
