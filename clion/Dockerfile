FROM debian:jessie
ARG HOST_USER

RUN apt-get update && apt-get install -y \
    wget sudo \

    # X11
    libx11-6 libxext-dev libxrender-dev libxtst-dev \

    # dependencies
    fontconfig git g++ gcc make \

    # JavaFX
    gtk2-engines libxtst6 libxxf86vm1 freeglut3 libxslt1.1

# user
ENV USER dev
RUN useradd -m -U $USER
RUN adduser $USER sudo
RUN echo "$USER ALL=(ALL) NOPASSWD:ALL" | tee -a /etc/sudoers
USER $USER
WORKDIR /home/$USER

# host SSH access
RUN echo "alias ssh-host=ssh\ ${HOST_USER}@\$(ip route list dev docker0 | awk 'NR==1 {print \$NF}')" >> .bashrc

# CLion
RUN mkdir clion/
RUN wget -O - https://download.jetbrains.com/cpp/CLion-2016.1.3.tar.gz | tar zx --strip-components=1 -C clion/

ENTRYPOINT ["clion/bin/clion.sh"]
