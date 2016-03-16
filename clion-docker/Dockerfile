FROM java:8
MAINTAINER Márcio Faustino

# update
RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get upgrade -y

# X11
RUN apt-get install -y libx11-6 libxext-dev libxrender-dev libxtst-dev

# toolchain
RUN apt-get install -y make gcc g++ git

# nicer fonts
RUN apt-get install -y fontconfig

# user
ENV USER dev
RUN apt-get -y install sudo
RUN useradd -m -U $USER
RUN adduser $USER sudo
RUN echo "$USER ALL=(ALL) NOPASSWD:ALL" | tee -a /etc/sudoers
USER $USER
WORKDIR /home/$USER
RUN mkdir opt

# CMake
RUN mkdir opt/cmake
RUN wget -O - https://cmake.org/files/v3.4/cmake-3.4.3-Linux-x86_64.tar.gz | tar zx --strip-components=1 -C opt/cmake
RUN echo 'export PATH=$PATH:$HOME/opt/cmake/bin' | tee -a .profile

# CLion
RUN mkdir opt/clion
RUN wget -O - https://download.jetbrains.com/cpp/clion-1.2.4.tar.gz | tar zx --strip-components=1 -C opt/clion
RUN echo 'export PATH=$PATH:$HOME/opt/clion/bin' | tee -a .profile

CMD opt/clion/bin/clion.sh
