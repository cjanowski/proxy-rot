#!/bin/bash
#
# PROXY ROT - Test IP Rotation
# Connects to each instance and tests the NAT IP
#

set -e

PROJECT_ID="boring-01"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║                PROXY ROT - IP ROTATION TEST                ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

REGIONS=("us-central1" "us-east1" "us-west1" "europe-west1" "asia-east1")
ZONES=("us-central1-a" "us-east1-b" "us-west1-a" "europe-west1-b" "asia-east1-a")

echo "Testing IP rotation across all regions..."
echo ""

for i in "${!REGIONS[@]}"; do
    REGION="${REGIONS[$i]}"
    ZONE="${ZONES[$i]}"
    INSTANCE="proxy-rot-instance-$REGION"
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Region: $REGION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Check if instance exists
    if ! gcloud compute instances describe "$INSTANCE" --zone="$ZONE" --project="$PROJECT_ID" &>/dev/null; then
        echo "✗ Instance not found: $INSTANCE"
        echo ""
        continue
    fi
    
    echo "Testing 5 requests from $INSTANCE..."
    echo ""
    
    # Run test on instance
    gcloud compute ssh "$INSTANCE" \
        --zone="$ZONE" \
        --project="$PROJECT_ID" \
        --command="for i in {1..5}; do echo \"Request \$i:\"; curl -s https://httpbin.org/ip | grep origin; sleep 1; done" \
        2>/dev/null
    
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✓ IP rotation test complete!"
echo ""
echo "Notice: Different requests show different IPs - that's rotation!"
echo ""

