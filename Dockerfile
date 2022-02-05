# General Config
FROM ubuntu:20.04
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV TZ US/Central
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone

# Update Environment
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y dist-upgrade
RUN apt-get -y autoremove

# Install python
RUN apt-get install -y python3-pip

# Install other apt packages
RUN apt-get -y install zip
RUN apt-get -y install git
RUN apt-get -y install graphviz
RUN apt-get -y install ffmpeg
RUN apt-get -y install libspatialindex-c6
RUN apt-get -y install tzdata

# Update git settings
RUN git config --global core.filemode false

# Install general packages
RUN pip3 install jupyter pandas numpy==1.20 requests matplotlib beautifulsoup4 statistics recordclass haversine sklearn 
RUN pip3 install gitpython pylint graphviz bs4 lxml flask html5lib geopandas shapely descartes click netaddr
RUN pip3 install pysal

# Install pytorch, see pytorch.org for updated command
RUN pip3 install torch==1.4.0+cpu torchvision==0.5.0+cpu -f https://download.pytorch.org/whl/torch_stable.html




