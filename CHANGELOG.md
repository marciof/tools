# 0.8.0 - UNRELEASED #

- Fix plugin "less" to count logical characters for line wrapping.

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
