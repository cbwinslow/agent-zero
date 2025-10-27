#!/bin/bash
set -e

echo "====================HACKING TOOLS INSTALLATION START===================="

# Update package list
apt-get update

# Install network reconnaissance tools
echo "Installing network reconnaissance tools..."
apt-get install -y --no-install-recommends \
    nmap \
    masscan \
    whois \
    dnsutils \
    netcat \
    tcpdump \
    net-tools \
    iputils-ping \
    traceroute

# Install web exploitation tools
echo "Installing web exploitation tools..."
apt-get install -y --no-install-recommends \
    curl \
    wget \
    nikto \
    dirb \
    sqlmap \
    wpscan

# Install password tools
echo "Installing password and hash tools..."
apt-get install -y --no-install-recommends \
    hashcat \
    john \
    hydra

# Install additional utilities
echo "Installing additional security utilities..."
apt-get install -y --no-install-recommends \
    binutils \
    steghide \
    exiftool \
    foremost \
    autopsy \
    sleuthkit

# Install Metasploit Framework (optional - commented out due to size)
# echo "Installing Metasploit Framework..."
# curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall
# chmod 755 msfinstall
# ./msfinstall
# rm msfinstall

# Clean up
apt-get clean
rm -rf /var/lib/apt/lists/*

echo "====================HACKING TOOLS INSTALLATION END===================="
