#!/bin/bash

## cleaning
sudo dpkg --configure -a
sudo apt purge -y google-chrome-stable
sudo apt autoremove -y
sudo apt clean
sudo rm -f /usr/local/bin/google-chrome
sudo rm -f /usr/local/bin/chromedriver
sudo rm -rf /opt/google/chrome

#### updating the system
sudo apt update -y
sudo apt upgrade -y

# Install necessary packages
sudo apt install -y unzip wget nano python3 python3-pip git

# Download Chrome 
wget "https://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.90-1_amd64.deb"
sudo apt install -y ./google-chrome-stable_114.0.5735.90-1_amd64.deb

# Download and set up ChromeDriver
wget "https://chromedriver.storage.googleapis.com/114.0.5735.16/chromedriver_linux64.zip"
unzip -o chromedriver_linux64.zip
sudo mv -f chromedriver /usr/local/bin/

### cleaning
sudo rm -f chromedriver_linux64.zip google-chrome-stable_114.0.5735.90-1_amd64.deb
sudo rm -f LICENSE.chromedriver

# Clone the repository and set permissions
git clone https://github.com/Dhiaeddine-Jraidi/aiesec_scraper.git
sudo chmod a+rwx aiesec_scraper

# Install Python dependencies
cd aiesec_scraper
sudo pip3 install -r requirements.txt

# Schedule running every 24 hours at 10 AM
(crontab -l 2>/dev/null; echo "0 10 * * * cd ~/aiesec_scraper && sudo python3 main.py >> ~/aiesec_scraper/output.log 2>&1") | crontab -



############## run the script using "sudo nohup bash "script_name".sh & "