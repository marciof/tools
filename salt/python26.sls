# Source:
# - http://askubuntu.com/a/141664/163034

python2.6:
  pkg.installed:
    - require:
      - pkgrepo: fkrull-deadsnakes

fkrull-deadsnakes:
  pkgrepo.managed:
    - ppa: fkrull/deadsnakes
