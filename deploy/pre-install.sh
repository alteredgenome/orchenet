#!/bin/bash
###############################################################################
# OrcheNet Pre-Installation Script
# For bare-bones Proxmox containers or minimal Debian installations
# Run this FIRST if install.sh fails due to missing basic utilities
###############################################################################

set -e

echo "=========================================="
echo "OrcheNet Pre-Installation Setup"
echo "For Minimal/Proxmox Containers"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Error: This script must be run as root"
    exit 1
fi

echo "Installing essential packages for minimal containers..."

# Update package lists
apt-get update

# Install absolutely essential packages first
apt-get install -y \
    sudo \
    procps \
    curl \
    wget \
    gnupg \
    ca-certificates \
    apt-transport-https

echo ""
echo "✓ Essential packages installed"
echo ""
echo "Now you can run the main installation:"
echo "  cd /root/orchenet/deploy"
echo "  ./install.sh"
echo ""
