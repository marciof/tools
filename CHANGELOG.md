# 0.11.0 - UNRELEASED #

- Plugin "diff": highlight changed words in unified diff input.
- Deactivate plugins automatically when unsupported.
- Fix broken pipe error when viewing very long output from programs and exiting early.
- Implicit option for plugins.
- Plugin "url": local file URLs.
- Fix plugin "pager" to respect the `PAGER` environment variable.

# 0.10.0 - 2016-07-20 #

- Plugin "vcs": show VCS revisions via `git`.
- Fix plugin "dir" to interpret inputs as paths only.
- Improve error handling and reporting.

# 0.9.0 - 2016-06-27 #

- Rename plugin "ls" to "dir" for readability.
- Rename plugin "less" back to "pager" for readability and because it does a lot more than just piping to `less`.

# 0.8.0 - 2016-05-30 #

- Automatically disable paging if reading input takes too long to finish.

# 0.7.0 - 2016-05-21 #

- Use `less` as the pager for systems that don't have `pager`.
- Fix exit code on option parsing errors.
- Fix exit code when a plugin has an error.
- Rename the disable plugin option to be more intuitive.

# 0.6.0 - 2016-05-10 #

- Plugin "pager": page output via `pager`.
- Fix plugin name check in options to accept only full matches, not prefixes.

# 0.5.0 - 2016-03-16 #

- Fix plugin "ls" redirection to honor the output type: TTY and non-TTY.

# 0.4.0 - 2016-03-04 #

- Plugin "file": read files.
- List directories piped through input.

# 0.3.0 - 2016-02-25 #

- Plugin "pipe": pipe input.

# 0.2.0 - 2016-02-20 #

- Option to disable specific plugins.

# 0.1.0 - 2016-02-13 #

- Plugin "ls": list directories via `ls`.
