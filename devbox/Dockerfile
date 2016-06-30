FROM debian:jessie
ARG HOST_USER

# base
RUN apt-get update && apt-get install -y apt-utils sudo wget

# dependencies
RUN apt-get update && apt-get install -y fontconfig git g++ gcc make

# X11
RUN apt-get update && apt-get install -y libx11-6 libxext-dev libxrender-dev libxtst-dev

# Java
RUN echo 'deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main' | tee /etc/apt/sources.list.d/webupd8team-java.list
RUN echo 'deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main' | tee -a /etc/apt/sources.list.d/webupd8team-java.list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886
RUN echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | debconf-set-selections
RUN apt-get update && apt-get install -y oracle-java8-installer

# JavaFX
RUN apt-get update && apt-get install -y gtk2-engines libxtst6 libxxf86vm1 freeglut3 libxslt1.1

# user
ENV USER dev
RUN useradd -m -U $USER
RUN adduser $USER sudo
RUN echo "$USER ALL=(ALL) NOPASSWD:ALL" | tee -a /etc/sudoers
USER $USER
WORKDIR /home/$USER

# host SSH access
# $ apt-get install ssh
# ~/.ssh/config (local): SendEnv BASHRC_HIDE_USER_HOST
# /etc/ssh/sshd_config (remote): AcceptEnv BASHRC_HIDE_USER_HOST
RUN echo "alias ssh-host=ssh\ ${HOST_USER}@\$(ip route list dev docker0 | awk 'NR==1 {print \$NF}')" >> .bashrc
RUN echo 'export BASHRC_HIDE_USER_HOST=x' >> .bashrc

# CLion
RUN mkdir clion/
RUN wget -O - https://download.jetbrains.com/cpp/CLion-2016.1.3.tar.gz | tar zx --strip-components=1 -C clion/

# IDEA
RUN mkdir idea/
RUN wget -O - https://download.jetbrains.com/idea/ideaIU-2016.1.3.tar.gz | tar zx --strip-components=1 -C idea/
