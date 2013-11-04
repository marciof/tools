# Source:
# - https://gist.github.com/renoirb/6722890
# - https://groups.google.com/forum/#!topic/salt-users/ynKNND9qxiI

oracle-java7-installer:
  pkg.installed:
    - require:
      - pkgrepo: webupd8-java
      - cmd: accept-oracle-license

webupd8-java:
  pkgrepo.managed:
    - ppa: webupd8team/java

accept-oracle-license:
  cmd.run:
    - unless: debconf-get-selections | grep -q shared/accepted-oracle-license-v1-1
    - name: echo oracle-java7-installer shared/accepted-oracle-license-v1-1 select true | debconf-set-selections
