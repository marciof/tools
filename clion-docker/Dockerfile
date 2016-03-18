FROM debian:jessie

# base
RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get upgrade -y
RUN apt-get install -y nano sudo wget

# X11
RUN apt-get install -y libx11-6 libxext-dev libxrender-dev libxtst-dev

# dependencies
RUN apt-get install -y fontconfig make gcc g++ git

# user
ENV USER dev
RUN useradd -m -U $USER
RUN adduser $USER sudo
RUN echo "$USER ALL=(ALL) NOPASSWD:ALL" | tee -a /etc/sudoers
USER $USER
WORKDIR /home/$USER

# CLion
RUN mkdir clion/
RUN wget -O - https://download.jetbrains.com/cpp/CLion-2016.1.tar.gz | tar zx --strip-components=1 -C clion/
RUN echo 'export PATH=$PATH:$HOME/clion/bin' | tee -a .profile

CMD clion/bin/clion.sh
