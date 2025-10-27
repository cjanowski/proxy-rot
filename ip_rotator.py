#!/usr/bin/env python3
"""
Cloud Proxy IP Rotator - Badass Edition

Prerequisites:
    1. Install required packages:
       pip install requests boto3 google-cloud-compute

    2. AWS Setup:
       - Deploy Terraform infrastructure: cd terraform-aws && terraform apply
       - AWS credentials must be configured for Terraform
       - Script reads endpoints from terraform-aws/terraform.tfstate

    3. GCP Setup (Optional):
       - Deploy Terraform infrastructure: cd terraform && ./deploy.sh
       - Install gcloud CLI: https://cloud.google.com/sdk/docs/install
       - Authenticate: `gcloud auth application-default login`
       - Set project: `gcloud config set project YOUR_PROJECT_ID`
"""

import sys
import time
import csv
import json
import subprocess
import os
from datetime import datetime
from typing import Optional, List, Dict

try:
    import requests
except ImportError as e:
    print("[ERROR] Missing required package. Run: pip install requests boto3")
    sys.exit(1)


# ASCII Art Banner
BANNER = """
        ╔════════════════════════════════════════════════════════════╗
        ║                                                            ║
        ║     ██████  ██████   ██████  ██   ██ ██    ██              ║
        ║     ██   ██ ██   ██ ██    ██  ██ ██   ██  ██               ║
        ║     ██████  ██████  ██    ██   ███     ████                ║
        ║     ██      ██   ██ ██    ██  ██ ██     ██                 ║
        ║     ██      ██   ██  ██████  ██   ██    ██                 ║
        ║                                                            ║
        ║     ██████   ██████  ████████                              ║
        ║     ██   ██ ██    ██    ██                                 ║
        ║     ██████  ██    ██    ██                                 ║
        ║     ██   ██ ██    ██    ██                                 ║
        ║     ██   ██  ██████     ██                                 ║
        ║                                                            ║
        ╚════════════════════════════════════════════════════════════╝
                         
              →  IP ROTATION ARSENAL  ←
                         
        ┌────────────────────────────────────────────────────────────┐
        │  STATUS: LOCKED & LOADED                                   │
        │  MODE: Automatic IP Cycling                                │
        │  PROVIDERS: AWS API Gateway | Google Cloud Platform        │
        └────────────────────────────────────────────────────────────┘
"""

MENU_BANNER = """
╔════════════════════════════════════════════════════════════════════╗
║                       SELECT CLOUD PROVIDER                        ║
╚════════════════════════════════════════════════════════════════════╝
"""


def print_separator(char="─", length=80):
    """Print a horizontal separator line."""
    print(char * length)


def print_box(message: str, width=80):
    """Print a message in a box."""
    padding = width - len(message) - 4
    left_pad = padding // 2
    right_pad = padding - left_pad
    print(f"║ {' ' * left_pad}{message}{' ' * right_pad} ║")


def print_status(status: str, message: str):
    """Print a status message with formatting."""
    status_colors = {
        "INFO": "►",
        "SUCCESS": "✓",
        "ERROR": "✗",
        "WAIT": "◆",
        "REQUEST": "→"
    }
    symbol = status_colors.get(status, "•")
    print(f"  {symbol} [{status:8s}] {message}")


def print_rotation_bar(current: int, total: int):
    """Print a rotation progress bar."""
    percentage = int((current / total) * 100)
    filled = int((current / total) * 20)
    bar = "▓" * filled + "░" * (20 - filled)
    print()
    print(f"              [{bar}]")
    print(f"                  ROTATING... {percentage}%")
    print()
    if current < total:
        print(f"         ⟳  Next rotation in progress...  ⟳")
    else:
        print(f"         ✓  All rotations complete!  ✓")
    print()


def extract_ip(response_json: dict) -> Optional[str]:
    """Extract IP address from httpbin.org response."""
    # httpbin.org/ip returns {"origin": "ip.address"}
    return response_json.get("origin", "Unknown")


def display_menu() -> str:
    """
    Display provider selection menu and get user choice.
    
    Returns:
        Selected provider ('aws' or 'gcp')
    """
    print(MENU_BANNER)
    print()
    print("  ┌═════════════════════════════════════════════════════════════════════════════┐")
    print("  │                                                                             │")
    print("  │    [1]  AWS API Gateway                                                     │")
    print("  │         → Uses Terraform-deployed API Gateway endpoints                     │")
    print("  │         → Requires: terraform-aws infrastructure deployed                   │")
    print("  │         → Rotates through 5 regional endpoints                              │")
    print("  │                                                                             │")
    print("  │    [2]  Google Cloud Platform                                               │")
    print("  │         → Uses GCP Compute Engine with multiple regions                     │")
    print("  │         → Requires: GCP project & gcloud authentication                     │")
    print("  │         → Cost: Variable (based on compute usage)                           │")
    print("  │                                                                             │")
    print("  │    [Q]  Quit                                                                │")
    print("  │                                                                             │")
    print("  └═════════════════════════════════════════════════════════════════════════════┘")
    print()
    
    while True:
        choice = input("  → Select provider [1/2/Q]: ").strip().lower()
        
        if choice in ['1', 'aws']:
            print()
            print_status("INFO", "Selected: AWS API Gateway")
            return 'aws'
        elif choice in ['2', 'gcp']:
            print()
            print_status("INFO", "Selected: Google Cloud Platform")
            return 'gcp'
        elif choice in ['q', 'quit', 'exit']:
            print()
            print_status("INFO", "Exiting...")
            sys.exit(0)
        else:
            print("  ✗ Invalid choice. Please enter 1, 2, or Q.")


def export_to_csv(proxy_data: List[Dict], filename: str = "proxy_ips.csv") -> bool:
    """
    Export proxy IP data to CSV file.
    
    Args:
        proxy_data: List of dictionaries containing proxy information
        filename: Output CSV filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['request_number', 'timestamp', 'ip_address', 'status_code', 'response_time_ms']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in proxy_data:
                writer.writerow(row)
        
        return True
    except Exception as e:
        print_status("ERROR", f"Failed to write CSV: {str(e)}")
        return False


def export_ips_to_txt(proxy_data: List[Dict], filename: str = "proxies.txt") -> bool:
    """
    Export just the IP addresses to a text file (one per line).
    
    Args:
        proxy_data: List of dictionaries containing proxy information
        filename: Output text filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w') as txtfile:
            for row in proxy_data:
                ip = row.get('ip_address', '')
                if ip and ip != 'Unknown':
                    txtfile.write(f"{ip}\n")
        
        return True
    except Exception as e:
        print_status("ERROR", f"Failed to write text file: {str(e)}")
        return False


def get_terraform_endpoints() -> List[str]:
    """
    Get API Gateway endpoints from Terraform outputs.
    
    Returns:
        List of API Gateway endpoint URLs
    """
    try:
        # Get the terraform-aws directory path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        terraform_dir = os.path.join(script_dir, 'terraform-aws')
        
        if not os.path.exists(terraform_dir):
            return []
        
        # Run terraform output command
        result = subprocess.run(
            ['terraform', 'output', '-json', 'api_endpoints_flat'],
            cwd=terraform_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            endpoints = json.loads(result.stdout)
            if isinstance(endpoints, list) and len(endpoints) > 0:
                return endpoints
        
        return []
        
    except Exception as e:
        print_status("ERROR", f"Failed to get Terraform endpoints: {str(e)}")
        return []


def run_aws_rotation(target_url: str, num_requests: int) -> List[Dict]:
    """
    Run IP rotation using AWS API Gateway.
    
    Args:
        target_url: Target URL to make requests to (e.g., https://httpbin.org/ip)
        num_requests: Number of requests to make
        
    Returns:
        List of proxy data dictionaries
    """
    proxy_data = []
    
    try:
        # Get Terraform-deployed endpoints
        print_status("WAIT", "Loading Terraform-deployed API Gateway endpoints...")
        print()
        
        endpoints = get_terraform_endpoints()
        
        if not endpoints:
            print_status("ERROR", "No Terraform endpoints found")
            print()
            print("Please ensure:")
            print("  • Terraform infrastructure is deployed: cd terraform-aws && terraform apply")
            print("  • Terraform state exists in terraform-aws/ directory")
            print()
            return proxy_data
        
        print_status("SUCCESS", f"Loaded {len(endpoints)} API Gateway endpoints")
        print()
        
        # Extract the path from target_url (e.g., /ip from https://httpbin.org/ip)
        from urllib.parse import urlparse
        parsed_url = urlparse(target_url)
        target_path = parsed_url.path if parsed_url.path else "/"
        
        print_status("INFO", f"Using {len(endpoints)} regional endpoints")
        print_status("INFO", f"Target path: {target_path}")
        print_separator()
        print()
        
        # Make requests and demonstrate IP rotation
        print("        ╔══════════════════════════════════════════════════════════╗")
        print("        ║         ROTATING IP DEMONSTRATION - AWS                  ║")
        print("        ╚══════════════════════════════════════════════════════════╝")
        print()
        
        session = requests.Session()
        
        for i in range(1, num_requests + 1):
            try:
                # Rotate through endpoints
                endpoint = endpoints[(i - 1) % len(endpoints)]
                
                # Construct the full URL: endpoint + target_path
                request_url = endpoint + target_path
                
                # Extract region from endpoint URL for display
                region = "unknown"
                if ".execute-api." in endpoint:
                    region = endpoint.split(".execute-api.")[1].split(".")[0]
                
                print_status("REQUEST", f"Request #{i}/{num_requests} - Region: {region}")
                
                # Make the request and track timing
                start_time = time.time()
                response = session.get(request_url, timeout=10)
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                response.raise_for_status()
                
                # Extract and display IP
                response_data = response.json()
                ip_address = extract_ip(response_data)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Store data for export
                proxy_data.append({
                    'request_number': i,
                    'timestamp': timestamp,
                    'ip_address': ip_address,
                    'status_code': response.status_code,
                    'response_time_ms': f"{response_time:.2f}"
                })
                
                print(f"            ┌{'─' * 60}┐")
                print(f"            │  Region: {region:<48} │")
                print(f"            │  IP Address: {ip_address:<44} │")
                print(f"            │  Status Code: {response.status_code:<43} │")
                print(f"            │  Response Time: {response_time:.2f} ms{' ' * (37 - len(f'{response_time:.2f}'))} │")
                print(f"            └{'─' * 60}┘")
                
                # Show rotation progress bar
                print_rotation_bar(i, num_requests)
                
                # Small delay between requests
                if i < num_requests:
                    time.sleep(0.5)
                
            except requests.exceptions.Timeout:
                print_status("ERROR", f"Request #{i} timed out")
                print()
            except requests.exceptions.RequestException as e:
                print_status("ERROR", f"Request #{i} failed: {str(e)}")
                print()
            except Exception as e:
                print_status("ERROR", f"Unexpected error on request #{i}: {str(e)}")
                print()
        
        print_separator()
        print()
        print_status("SUCCESS", "All requests completed")
        print()
        
    except Exception as e:
        print()
        print_status("ERROR", f"AWS error: {str(e)}")
        print()
        print("Troubleshooting tips:")
        print("  • Verify Terraform infrastructure is deployed")
        print("  • Check terraform-aws/terraform.tfstate exists")
        print("  • Ensure AWS API Gateway endpoints are accessible")
        print()
        
    return proxy_data


def run_gcp_rotation(target_url: str, num_requests: int) -> List[Dict]:
    """
    Run IP rotation using Google Cloud Platform.
    
    Args:
        target_url: Target URL to make requests to
        num_requests: Number of requests to make
        
    Returns:
        List of proxy data dictionaries
    """
    import subprocess
    import json
    
    proxy_data = []
    
    print_status("INFO", "GCP rotation mode selected")
    print()
    
    # GCP regions and zones to rotate through
    gcp_regions = [
        ('us-central1', 'us-central1-a'),
        ('us-east1', 'us-east1-b'),
        ('us-west1', 'us-west1-a'),
        ('europe-west1', 'europe-west1-b'),
        ('asia-east1', 'asia-east1-a')
    ]
    
    # Check if gcloud is available
    try:
        subprocess.run(['gcloud', '--version'], 
                      capture_output=True, 
                      check=True, 
                      timeout=5)
        gcloud_available = True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        gcloud_available = False
        print_status("WARN", "gcloud CLI not found - using direct HTTP requests")
        print_status("INFO", "For true GCP rotation, ensure Terraform infra is deployed")
        print()
    
    try:
        print("        ╔══════════════════════════════════════════════════════════╗")
        print("        ║         ROTATING IP DEMONSTRATION - GCP                  ║")
        print("        ╚══════════════════════════════════════════════════════════╝")
        print()
        
        if gcloud_available:
            print_status("INFO", "Using GCP Cloud NAT instances for TRUE rotation")
            print_status("INFO", f"Rotating through {len(gcp_regions)} regions")
        else:
            print_status("INFO", "Using direct HTTP requests (simulated rotation)")
            print_status("INFO", "Deploy Terraform infrastructure for true rotation")
        print()
        
        for i in range(1, num_requests + 1):
            try:
                region, zone = gcp_regions[i % len(gcp_regions)]
                instance_name = f"proxy-rot-instance-{region}"
                
                print_status("REQUEST", f"Request #{i}/{num_requests} - Region: {region}")
                
                start_time = time.time()
                
                if gcloud_available:
                    # Make request through GCP instance via gcloud ssh
                    cmd = [
                        'gcloud', 'compute', 'ssh', instance_name,
                        '--zone', zone,
                        '--project', 'boring-01',
                        '--command', f'curl -s {target_url}',
                        '--quiet'
                    ]
                    
                    try:
                        result = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=15,
                            check=True
                        )
                        response_time = (time.time() - start_time) * 1000
                        
                        # Parse the response
                        response_data = json.loads(result.stdout)
                        ip_address = extract_ip(response_data)
                        status_code = 200
                        
                    except subprocess.TimeoutExpired:
                        print_status("ERROR", f"Request timed out for {region}")
                        print()
                        continue
                    except subprocess.CalledProcessError as e:
                        print_status("ERROR", f"Instance {instance_name} not accessible")
                        print_status("INFO", "Ensure Terraform infrastructure is deployed")
                        print()
                        continue
                    except json.JSONDecodeError:
                        print_status("ERROR", f"Invalid response from {region}")
                        print()
                        continue
                        
                else:
                    # Fall back to direct request
                    response = requests.get(target_url, timeout=10)
                    response_time = (time.time() - start_time) * 1000
                    response.raise_for_status()
                    
                    response_data = response.json()
                    ip_address = extract_ip(response_data)
                    status_code = response.status_code
                
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Store data for CSV export
                proxy_data.append({
                    'request_number': i,
                    'timestamp': timestamp,
                    'ip_address': ip_address,
                    'status_code': status_code,
                    'response_time_ms': f"{response_time:.2f}"
                })
                
                print(f"            ┌{'─' * 60}┐")
                print(f"            │  Region: {region:<48} │")
                print(f"            │  IP Address: {ip_address:<44} │")
                print(f"            │  Status Code: {status_code:<43} │")
                print(f"            │  Response Time: {response_time:.2f} ms{' ' * (37 - len(f'{response_time:.2f}'))} │")
                print(f"            └{'─' * 60}┘")
                
                # Show rotation progress bar
                print_rotation_bar(i, num_requests)
                
                # Small delay between requests
                if i < num_requests:
                    time.sleep(0.5)
                
            except requests.exceptions.Timeout:
                print_status("ERROR", f"Request #{i} timed out")
                print()
            except requests.exceptions.RequestException as e:
                print_status("ERROR", f"Request #{i} failed: {str(e)}")
                print()
            except Exception as e:
                print_status("ERROR", f"Unexpected error on request #{i}: {str(e)}")
                print()
        
        print_separator()
        print()
        print_status("SUCCESS", "All requests completed")
        print()
        
        if not gcloud_available:
            print_status("INFO", "For TRUE IP rotation:")
            print("          1. Deploy Terraform infrastructure: cd terraform && ./deploy.sh")
            print("          2. Ensure gcloud CLI is installed and authenticated")
            print("          3. Run PROXY ROT again to use deployed instances")
            print()
        
    except Exception as e:
        print()
        print_status("ERROR", f"GCP error: {str(e)}")
        print()
        
    return proxy_data


def main():
    """Main execution function."""
    # Print banner
    print(BANNER)
    print()
    
    # Display menu and get provider choice
    provider = display_menu()
    print_separator()
    print()
    
    # Configuration
    target_url = "https://httpbin.org/ip"
    num_requests = 5
    
    # Storage for proxy data
    proxy_data = []
    
    print_status("INFO", f"Provider: {provider.upper()}")
    print_status("INFO", f"Target URL: {target_url}")
    print_status("INFO", f"Number of requests: {num_requests}")
    print_status("INFO", f"Export: proxies.txt (optional)")
    print_separator()
    print()
    
    # Run the appropriate rotation based on provider
    if provider == 'aws':
        proxy_data = run_aws_rotation(target_url, num_requests)
    elif provider == 'gcp':
        proxy_data = run_gcp_rotation(target_url, num_requests)
    else:
        print_status("ERROR", f"Unknown provider: {provider}")
        sys.exit(1)
    
    # Export to proxies.txt
    if proxy_data:
        print_separator()
        print()
        print("        ╔══════════════════════════════════════════════════════════╗")
        print("        ║              EXPORT PROXY LIST                           ║")
        print("        ╚══════════════════════════════════════════════════════════╝")
        print()
        print(f"            Total IPs collected: {len(proxy_data)}")
        print()
        
        # Ask if user wants to export IPs to text file
        txt_choice = input("  → Export IP list to proxies.txt? [Y/n]: ").strip().lower()
        
        if txt_choice in ['', 'y', 'yes']:
            print()
            print_status("WAIT", "Exporting IPs to proxies.txt...")
            if export_ips_to_txt(proxy_data, "proxies.txt"):
                print_status("SUCCESS", "IPs exported: proxies.txt")
                print(f"            Format: One IP per line")
                print(f"            Total: {len(proxy_data)} IPs")
            print()
        else:
            print()
            print_status("INFO", "Export skipped")
            print()
    else:
        print_status("ERROR", "No proxy data collected")
        print()
    
    print_separator("═")
    print_box("PROXY ROTATION COMPLETE", 80)
    print_separator("═")


if __name__ == "__main__":
    main()
