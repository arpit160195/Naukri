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
    wget \
    unzip \
    curl \
    gnupg \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libpangocairo-1.0-0 \
    libxss1 \
    fonts-liberation \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm-dev \
    && rm -rf /var/lib/apt/lists/* \

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y google-chrome-stable \

# Install ChromeDriver
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip

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
CMD ["/bin/bash", "-c", "source .venv/bin/activate && python naukri.py"]