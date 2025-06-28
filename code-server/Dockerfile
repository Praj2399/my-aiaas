FROM ubuntu:22.04

# Set environment variables for non-interactive apt and rust installation
ENV DEBIAN_FRONTEND=noninteractive
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH

# Install system dependencies
RUN apt update && apt install -y \
    curl \
    wget \
    git \
    unzip \
    sudo \
    build-essential \
    python3.10 \
    python3.10-venv \
    python3.10-distutils \
    python3-pip \
    ca-certificates \
    software-properties-common \
    libssl-dev \
    pkg-config
# Install Docker CLI
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
    gpg --dearmor -o /etc/apt/keyrings/docker.gpg

RUN echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
    https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
    > /etc/apt/sources.list.d/docker.list

RUN apt-get update && apt-get install -y docker-ce-cli

# Set Python 3.10 as default
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Install Rust (for building packages like sudachipy)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# Ensure rust/cargo is available for pip
ENV PATH="/usr/local/cargo/bin:$PATH"

# Install code-server (latest)
RUN curl -fsSL https://code-server.dev/install.sh | sh

# Set working directory
WORKDIR /root

# Copy requirements file
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip && pip install --no-cache-dir --ignore-installed -r requirements.txt

# Expose code-server port
EXPOSE 8080

# Run code-server
CMD ["code-server", "--bind-addr", "0.0.0.0:8080", "--auth", "password"]
