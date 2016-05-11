FROM debian:jessie

# base
RUN apt-get update && apt-get install -y apt-utils wget

# X11
RUN apt-get install -y libx11-6 libxext-dev libxrender-dev libxtst-dev

# dependencies
RUN apt-get install -y fontconfig git g++ gcc make

# user
RUN apt-get install -y sudo
ENV USER dev
RUN useradd -m -U $USER
RUN adduser $USER sudo
RUN echo "$USER ALL=(ALL) NOPASSWD:ALL" | tee -a /etc/sudoers
USER $USER
WORKDIR /home/$USER

# CLion
RUN mkdir clion/
RUN wget -O - https://download.jetbrains.com/cpp/CLion-2016.1.2.tar.gz | tar zx --strip-components=1 -C clion/

ENTRYPOINT ["clion/bin/clion.sh"]
