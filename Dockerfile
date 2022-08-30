##############################################################################
# Dockerfile to run MXCuBE web server
##############################################################################

FROM debian:11
LABEL author="Marcus Oscarsson <marcus.oscarsson@esrf.fr>"
LABEL maintainer="ANSTO, Clayton Synchrotron"

ENV PATH /opt/conda/bin:$PATH
ENV TERM linux
ENV USER root

# Set BL_ACTIVE to true to use real devices
ENV BL_ACTIVE=true
ENV AUTO_FAKE=false

# Simplon API host and port
ENV DECTRIS_DETECTOR_HOST=sim_plon_api
ENV DECTRIS_DETECTOR_PORT=8080

# Install system packages
RUN apt update --fix-missing && apt -y upgrade && \
  apt install -y apt-utils curl git sudo build-essential wget vim \
  bzip2 ca-certificates libglib2.0-0 libxext6 libsm6 libxrender1 \
  libgl1-mesa-glx libxi6 libsasl2-dev python-dev libldap2-dev libssl-dev

RUN wget --quiet https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
  /bin/bash ~/miniconda.sh -b -p /opt/conda && \
  rm ~/miniconda.sh

RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> ~/.bashrc && \
  echo "conda activate base" >> ~/.bashrc

RUN ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh

RUN conda init bash

WORKDIR /opt

# Define conda environment and Install local MXCuBE3
COPY .git /opt/.git
COPY . /opt/mxcube3
ENV CONDA_ENV mxcube
RUN conda update -y -n base -c defaults conda
RUN conda env create -f /opt/mxcube3/conda-environment.yml

RUN conda init bash && . ~/.bashrc && conda activate $CONDA_ENV && \
  pip install -i https://pypi.asci.synchrotron.org.au/root/pypi/+simple \
  --extra-index-url https://pypi.asci.synchrotron.org.au/mx3/dev \
  --extra-index-url https://pypi.asci.synchrotron.org.au/asci/prod/+simple \
  -r /opt/mxcube3/requirements.txt && \
  python /opt/mxcube3/docker/mxcubecore_copy_script.py

# Set EPICS NAMESERVER address to access PVs on the MX3 network
ENV EPICS_CA_ADDR_LIST=10.244.101.10

COPY docker/mxcube /usr/local/bin/
COPY docker/docker-entrypoint.sh /usr/local/bin/
RUN chmod 765 /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["/bin/bash"]

EXPOSE 8090 8081
