#!/bin/bash
#
# PROXY ROT - Quick Live Rotation Test
# Tests your deployed GCP infrastructure
#

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║           PROXY ROT - LIVE ROTATION TEST                  ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

PROJECT_ID="boring-01"
REGIONS=("us-central1" "us-east1" "us-west1" "europe-west1" "asia-east1")
ZONES=("us-central1-a" "us-east1-b" "us-west1-a" "europe-west1-b" "asia-east1-a")

echo "Testing TRUE IP rotation across your deployed infrastructure..."
echo ""
echo "Your NAT IPs should rotate through these addresses:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
## Add the IPs here
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Running 15 requests (3 per region)..."
echo ""

for i in {1..15}; do
    REGION_IDX=$(( (i - 1) % 5 ))
    REGION="${REGIONS[$REGION_IDX]}"
    ZONE="${ZONES[$REGION_IDX]}"
    INSTANCE="proxy-rot-instance-$REGION"
    
    echo "→ Request #$i - Region: $REGION"
    
    IP=$(gcloud compute ssh "$INSTANCE" \
        --zone="$ZONE" \
        --project="$PROJECT_ID" \
        --command="curl -s https://httpbin.org/ip | grep -oP '\"origin\": \"\K[^\"]+'" \
        --quiet 2>/dev/null || echo "FAILED")
    
    if [ "$IP" != "FAILED" ]; then
        echo "  ✓ IP: $IP"
    else
        echo "  ✗ Request failed"
    fi
    
    echo ""
    
    # Small delay between requests
    sleep 0.5
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✓ Rotation test complete!"
echo ""
echo "Notice: IPs should match those from your NAT pool above."
echo "        Each region rotates through its 3 assigned IPs."
echo ""
echo "To use this in PROXY ROT Python script:"
echo "  python ip_rotator.py"
echo "  Select option [2] for GCP"
echo ""

