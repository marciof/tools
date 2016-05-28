This project adheres to [Semantic Versioning](http://semver.org).

# Dependencies #

See `.travis.yml` for details.

# To Do #

- Count logical characters for paging instead of bytes.
- Allow line numbers in input names to scroll to when paging.
- Size mismatch issue with argv as Arrays?
- Code coverage.
- Profile each change.
  - http://geoff.greer.fm/ag/speed/
  - Reduce memory allocation.
  - `./bin/callgrind -p less:-E -p less:+$(wc -l < /var/log/syslog.1) /var/log/syslog.1`
