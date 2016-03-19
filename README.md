This project adheres to [Semantic Versioning](http://semver.org).

# Dependencies #

## Build ##

- [CMake](https://cmake.org) >= 3.4

## Test ##

- [Python](https://www.python.org) >= 3
- [libcheck](http://libcheck.github.io/check/)
- [perf](https://perf.wiki.kernel.org)
- [Valgrind](http://valgrind.org)
- [Callgrind](https://kcachegrind.github.io)

# To Do #

- Tests with coverage.
  - http://rr-project.org
  - https://autotest.github.io
  - https://github.com/andrewrk/malcheck
- Profile each commit.
  - http://geoff.greer.fm/ag/speed/
  - Reduce memory allocation.
- Continuous integration.
  - https://scan.coverity.com
  - https://travis-ci.org
- Lint and static analysis?
  - http://clang-analyzer.llvm.org
