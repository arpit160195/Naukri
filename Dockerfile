# Use BuildKit secrets
# syntax=docker/dockerfile:1.2
FROM ubuntu:latest

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    openssh-client \
    wget \
    curl \
    unzip \
    python3 \
    python3-venv \
    python3-pip

# Set non-interactive mode for APT commands
ENV DEBIAN_FRONTEND=noninteractive

# Install Chrome
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg && \
    wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
# Kill any running Chrome instances
    pkill chrome || true && \
# Clean up
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Setup SSH directory
RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh

# Copy SSH Key
COPY id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

# Clone the private repository
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts && \
    GIT_SSH_COMMAND="ssh -i /root/.ssh/id_rsa -o StrictHostKeyChecking=no" git clone git@github.com:arpit160195/Naukri.git /app

# Remove SSH key for security
RUN rm -f /root/.ssh/id_rsa

# Set working directory
WORKDIR /app

# Debug: Check if cloning worked
RUN ls -la /app

# Set up Python virtual environment and install dependencies
RUN python3 -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install -r requirements.txt

# Set entrypoint (optional)
CMD [".venv/bin/python", "naukri.py"]