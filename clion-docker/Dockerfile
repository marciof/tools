FROM debian:jessie
MAINTAINER Márcio Faustino

# base
RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get upgrade -y
RUN apt-get install -y nano sudo wget

# X11
RUN apt-get install -y libx11-6 libxext-dev libxrender-dev libxtst-dev

# toolchain
RUN apt-get install -y make gcc g++ git

# fonts
RUN apt-get install -y fontconfig

# user
ENV USER dev
RUN useradd -m -U $USER
RUN adduser $USER sudo
RUN echo "$USER ALL=(ALL) NOPASSWD:ALL" | tee -a /etc/sudoers
USER $USER
WORKDIR /home/$USER

# CLion
RUN mkdir -p opt/clion
RUN wget -O - https://download.jetbrains.com/cpp/CLion-2016.1.tar.gz | tar zx --strip-components=1 -C opt/clion
RUN echo 'export PATH=$PATH:$HOME/opt/clion/bin' | tee -a .profile

CMD opt/clion/bin/clion.sh
