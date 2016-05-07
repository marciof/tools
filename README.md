This project adheres to [Semantic Versioning](http://semver.org).

# Dependencies #

See `.travis.yml` for details.

# To Do #

- Use simple C strings to avoid storing buffer lengths separately?
- Lint and static analysis?
  - http://clang-analyzer.llvm.org
- Profile each commit.
  - http://geoff.greer.fm/ag/speed/
  - Reduce memory allocation.
- Tests with coverage.
  - https://github.com/andrewrk/malcheck
  - https://github.com/google/sanitizers
- Use `libpipeline` to simplify the code?
