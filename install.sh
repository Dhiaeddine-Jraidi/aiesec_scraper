#!/bin/bash

sudo apt update
sudo apt upgrade
sudo apt install -y unzip wget nano python3 python3-pip git
sudo apt purge -y google-chrome-stable
sudo rm -f /usr/local/bin/google-chrome
sudo rm -f /usr/local/bin/chromedriver
wget https://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/google-chrome-stable_114.0.5735.90-1_amd64.deb
sudo apt install -y ./google-chrome-stable_114.0.5735.90-1_amd64.deb
wget "https://chromedriver.storage.googleapis.com/114.0.5735.16/chromedriver_linux64.zip"
unzip -o chromedriver_linux64.zip
sudo mv -f chromedriver /usr/local/bin/
sudo rm -f chromedriver_linux64.zip google-chrome-stable_114.0.5735.90-1_amd64.deb
echo "Chrome version 114.0.5735.90 and Chrome WebDriver version 114.0.5735.16 installation completed successfully!"
git clone https://github.com/Dhiaeddine-Jraidi/aiesec_scraper.git
sudo chmod a+rwx aiesec_scraper
cd aiesec_scraper
pip3 install -r requirements.txt
(crontab -l 2>/dev/null; echo "0 0 * * * cd ~/aiesec_scraper && python3 main.py") | crontab -
