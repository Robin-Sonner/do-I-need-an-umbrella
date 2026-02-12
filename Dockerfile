FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install PyQt6 dependencies
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    apt-get install -y \
    libxcb-cursor0 \
    libgl1 \
    libxkbcommon-x11-0 \
    libglx-mesa0 \
    libegl1 \
    libfontconfig1 \
    libxcb-xkb1 \
    libxcb-icccm4 \
    libxcb-keysyms1 \
    libxcb-shape0 \
    fonts-noto-color-emoji \
    fonts-noto \
    fontconfig

# Install Python 3.13
RUN add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.13 python3.13-venv

WORKDIR /app
COPY . .

# Create a virtual environment and build the package
RUN python3.13 -m venv venv && \
    . venv/bin/activate && \
    pip install --upgrade pip && \
    pip install ".[dev,gui]"

# Activate virtual environment in the shell
ENV PATH="/app/venv/bin:$PATH"

# Create Jupyter config directory
RUN mkdir -p /root/.jupyter

# Configure the jupyter notebook
RUN echo "c.ServerApp.ip = '0.0.0.0'" >> /root/.jupyter/jupyter_server_config.py && \
    echo "c.ServerApp.open_browser = False" >> /root/.jupyter/jupyter_server_config.py && \
    echo "c.ServerApp.allow_root = True" >> /root/.jupyter/jupyter_server_config.py && \
    echo "c.ServerApp.token = ''" >> /root/.jupyter/jupyter_server_config.py && \
    echo "c.ServerApp.password = ''" >> /root/.jupyter/jupyter_server_config.py

CMD ["/bin/bash"]
