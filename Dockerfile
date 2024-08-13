# Use an official Ubuntu as a parent image
FROM ubuntu:latest

# Set the working directory
WORKDIR /app

# Copy the application code into the image
COPY . /app

# Update and install dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
        unzip \
        wget \
        python3 \
        python3-pip \
        python3-venv \
        && \
    python3 -m venv .venv && \
    . .venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && \
    wget "https://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.90-1_amd64.deb" && \
    apt install -y ./google-chrome-stable_114.0.5735.90-1_amd64.deb && \
    wget "https://chromedriver.storage.googleapis.com/114.0.5735.16/chromedriver_linux64.zip" && \
    unzip -o chromedriver_linux64.zip -d /usr/local/bin/ && \
    rm -f chromedriver_linux64.zip google-chrome-stable_114.0.5735.90-1_amd64.deb

EXPOSE 8080

CMD [".venv/bin/python3", "main.py"]