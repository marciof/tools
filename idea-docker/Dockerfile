FROM debian:jessie

# base
RUN apt-get update
RUN apt-get install -y apt-utils wget

# X11
RUN apt-get install -y libx11-6 libxext-dev libxrender-dev libxtst-dev

# dependencies
RUN apt-get install -y fontconfig git

# Java
RUN echo 'deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main' | tee /etc/apt/sources.list.d/webupd8team-java.list
RUN echo 'deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main' | tee -a /etc/apt/sources.list.d/webupd8team-java.list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886
RUN apt-get update
RUN echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | debconf-set-selections
RUN apt-get install -y oracle-java8-installer

# user
RUN apt-get install -y sudo
ENV USER dev
RUN useradd -m -U $USER
RUN adduser $USER sudo
RUN echo "$USER ALL=(ALL) NOPASSWD:ALL" | tee -a /etc/sudoers
USER $USER
WORKDIR /home/$USER

# IDEA
RUN mkdir idea/
RUN wget -O - https://download.jetbrains.com/idea/ideaIU-2016.1.1.tar.gz | tar zx --strip-components=1 -C idea/

ENTRYPOINT ["idea/bin/idea.sh"]
