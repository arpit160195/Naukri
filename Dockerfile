# Use the official Python base image
FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Set a default DISPLAY for Xvfb
ENV DISPLAY=:99
# Set the timezone to IST for your application
ENV TZ=Asia/Kolkata

# Install system dependencies including Xvfb
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    curl \
    unzip \
    gnupg \
    xvfb \
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
    libgbm-dev && \
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome-keyring.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && apt-get install -y --no-install-recommends google-chrome-stable && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Create /tmp/.X11-unix with proper permissions Before switching to non-root
RUN mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix

# Install pip and undetected_chromedriver
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir undetected-chromedriver==3.1.5.post4

# (Optional) Set locale if needed
ENV LANG C.UTF-8

# Download the correct ChromeDriver for Chrome version 134 using Bash explicitly.
RUN /bin/bash -c 'mkdir -p /appenv && \
    CHROMEDRIVER_VERSION="134.0.6998.88" && \
    echo "Using ChromeDriver version: ${CHROMEDRIVER_VERSION}" && \
    wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROMEDRIVER_VERSION}/linux64/chromedriver-linux64.zip && \
    unzip -j /tmp/chromedriver.zip -d /appenv/ && \
    chmod +x /appenv/chromedriver && \
    rm /tmp/chromedriver.zip'

# Patch ChromeDriver
RUN python -c "from undetected_chromedriver.patcher import Patcher; \
    patcher = Patcher(executable_path='/appenv/chromedriver', version_main=114); \
    success = patcher.auto(); \
    print(f'Patching status: {success}'); \
    assert success, 'ChromeDriver patching failed!'"


# Create the Naukri project directory and set it as the working directory
RUN mkdir -p /Naukri
WORKDIR /Naukri

# Copy application scripts and dependencies
COPY naukri.py .
COPY requirements.txt .
COPY ArpitCV.pdf .

# Install Python application dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add a non-root user for security
RUN useradd -m nonrootuser && chown -R nonrootuser /Naukri
USER nonrootuser

# Set the entrypoint to run the main Python script
ENTRYPOINT ["python", "naukri.py"]