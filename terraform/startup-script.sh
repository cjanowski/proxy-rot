#!/bin/bash
#
# PROXY ROT - Instance Startup Script
# Configures proxy rotation instance
#

set -e

# Update system
apt-get update
apt-get install -y \
    python3 \
    python3-pip \
    curl \
    wget \
    net-tools \
    iptables

# Install Python packages for proxy rotation
pip3 install requests

# Create a simple proxy test script
cat > /opt/proxy_test.py <<'EOF'
#!/usr/bin/env python3
"""
PROXY ROT - Test script to verify NAT IP rotation
"""
import requests
import time

def test_external_ip():
    """Test what external IP we're using"""
    try:
        response = requests.get('https://httpbin.org/ip', timeout=10)
        data = response.json()
        print(f"External IP: {data.get('origin', 'Unknown')}")
        return data.get('origin')
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    print("PROXY ROT - IP Rotation Test")
    print("-" * 50)
    
    for i in range(5):
        print(f"\nRequest #{i+1}:")
        test_external_ip()
        time.sleep(2)
EOF

chmod +x /opt/proxy_test.py

# Enable IP forwarding
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

# Log startup completion
echo "PROXY ROT instance initialized at $(date)" >> /var/log/proxy-rot-init.log
echo "Instance ready for IP rotation" >> /var/log/proxy-rot-init.log

