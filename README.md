This project adheres to [Semantic Versioning](http://semver.org).

# Dependencies #

See `.travis.yml` for details.

# To Do #

- Split plugins into input and output? To simplify and to avoid having to memory allocate outputs.
- Code coverage.
- Profile each change.
  - http://geoff.greer.fm/ag/speed/
  - Reduce memory allocation.
  - `./bin/callgrind -p pager:-E -p pager:+$(wc -l < /var/log/syslog.1) /var/log/syslog.1`
- Count logical characters for paging instead of bytes.
- Allow line numbers in input names to scroll to when paging.
