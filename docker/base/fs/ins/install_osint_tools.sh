#!/bin/bash
set -e

echo "====================OSINT TOOLS INSTALLATION START===================="

# Install basic OSINT and reconnaissance tools
apt-get install -y --no-install-recommends \
    nmap \
    whois \
    dnsutils \
    netcat-traditional \
    curl \
    wget \
    git \
    jq \
    bind9-dnsutils \
    traceroute \
    tcpdump \
    net-tools \
    iproute2 \
    iputils-ping \
    openssh-client \
    telnet

echo "====================OSINT TOOLS: Installing Python-based tools===================="

# Install Python OSINT libraries
pip3 install --no-cache-dir \
    shodan \
    censys \
    requests \
    dnspython \
    python-whois \
    builtwith \
    ipwhois \
    phonenumbers

echo "====================OSINT TOOLS: Installing theHarvester===================="

# Install theHarvester (email harvesting tool)
cd /opt
git clone --depth=1 https://github.com/laramies/theHarvester.git || true
cd theHarvester
pip3 install -r requirements.txt || true

echo "====================OSINT TOOLS: Installing Sublist3r===================="

# Install Sublist3r (subdomain enumeration)
cd /opt
git clone --depth=1 https://github.com/aboul3la/Sublist3r.git || true
cd Sublist3r
pip3 install -r requirements.txt || true

echo "====================OSINT TOOLS: Installing Amass===================="

# Install Amass (subdomain enumeration and network mapping)
cd /tmp
wget -q https://github.com/owasp-amass/amass/releases/download/v4.2.0/amass_Linux_amd64.zip || true
unzip -q amass_Linux_amd64.zip || true
mv amass_Linux_amd64/amass /usr/local/bin/ || true
rm -rf amass_Linux_amd64.zip amass_Linux_amd64 || true

echo "====================OSINT TOOLS: Installing Subfinder===================="

# Install Subfinder (subdomain discovery tool)
cd /tmp
wget -q https://github.com/projectdiscovery/subfinder/releases/download/v2.6.3/subfinder_2.6.3_linux_amd64.zip || true
unzip -q subfinder_2.6.3_linux_amd64.zip || true
mv subfinder /usr/local/bin/ || true
rm -rf subfinder_2.6.3_linux_amd64.zip || true

echo "====================OSINT TOOLS: Installing Nuclei===================="

# Install Nuclei (vulnerability scanner)
cd /tmp
wget -q https://github.com/projectdiscovery/nuclei/releases/download/v3.1.0/nuclei_3.1.0_linux_amd64.zip || true
unzip -q nuclei_3.1.0_linux_amd64.zip || true
mv nuclei /usr/local/bin/ || true
rm -rf nuclei_3.1.0_linux_amd64.zip || true

echo "====================OSINT TOOLS: Installing HTTPx===================="

# Install HTTPx (HTTP probe tool)
cd /tmp
wget -q https://github.com/projectdiscovery/httpx/releases/download/v1.3.7/httpx_1.3.7_linux_amd64.zip || true
unzip -q httpx_1.3.7_linux_amd64.zip || true
mv httpx /usr/local/bin/ || true
rm -rf httpx_1.3.7_linux_amd64.zip || true

echo "====================OSINT TOOLS: Installing Masscan===================="

# Install Masscan (fast port scanner)
apt-get install -y --no-install-recommends masscan || true

echo "====================OSINT TOOLS: Installing Nikto===================="

# Install Nikto (web server scanner)
apt-get install -y --no-install-recommends nikto || true

echo "====================OSINT TOOLS: Installing SQLMap===================="

# Install SQLMap (SQL injection tool)
apt-get install -y --no-install-recommends sqlmap || true

echo "====================OSINT TOOLS: Installing WPScan===================="

# Install WPScan (WordPress security scanner)
apt-get install -y --no-install-recommends wpscan || true

echo "====================OSINT TOOLS: Installing DirBuster/GoBuster===================="

# Install GoBuster (directory/file brute forcing)
apt-get install -y --no-install-recommends gobuster || true

echo "====================OSINT TOOLS: Installing MetaSploit prerequisites===================="

# Install tools that work with Metasploit
apt-get install -y --no-install-recommends \
    postgresql \
    postgresql-contrib || true

echo "====================OSINT TOOLS: Installing Social Engineering tools===================="

# Install Social Engineering toolkit prerequisites
pip3 install --no-cache-dir \
    pwnedpasswords \
    social-analyzer || true

echo "====================OSINT TOOLS: Installing Recon-ng===================="

# Install Recon-ng (web reconnaissance framework)
cd /opt
git clone --depth=1 https://github.com/lanmaster53/recon-ng.git || true
cd recon-ng
pip3 install -r REQUIREMENTS || true

echo "====================OSINT TOOLS: Installing Sherlock===================="

# Install Sherlock (username search across social media)
cd /opt
git clone --depth=1 https://github.com/sherlock-project/sherlock.git || true
cd sherlock
pip3 install -r requirements.txt || true

echo "====================OSINT TOOLS: Installing SpiderFoot===================="

# Install SpiderFoot (OSINT automation)
cd /opt
git clone --depth=1 https://github.com/smicallef/spiderfoot.git || true
cd spiderfoot
pip3 install -r requirements.txt || true

echo "====================OSINT TOOLS: Cleanup===================="

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

echo "====================OSINT TOOLS INSTALLATION END===================="
