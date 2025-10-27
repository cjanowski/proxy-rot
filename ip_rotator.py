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


# ANSI Color Codes
class Colors:
    # Reset
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    
    # Gradient colors (custom 256-color palette)
    @staticmethod
    def rgb(r, g, b):
        """Generate 24-bit RGB color code."""
        return f'\033[38;2;{r};{g};{b}m'
    
    @staticmethod
    def bg_rgb(r, g, b):
        """Generate 24-bit RGB background color code."""
        return f'\033[48;2;{r};{g};{b}m'


def strip_ansi(text):
    """Remove ANSI color codes from text to get visible length."""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def visible_length(text):
    """Get the visible length of text (excluding ANSI codes)."""
    return len(strip_ansi(text))


def gradient_text(text, start_color, end_color):
    """Apply gradient effect to text."""
    if len(text) == 0:
        return text
    
    result = []
    length = len(text)
    
    for i, char in enumerate(text):
        # Calculate interpolated color
        ratio = i / max(length - 1, 1)
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        
        result.append(f'{Colors.rgb(r, g, b)}{char}')
    
    result.append(Colors.RESET)
    return ''.join(result)


# ASCII Art Banner with gradients
def print_banner():
    """Print stylized banner with gradients."""
    cyan_to_blue = lambda text: gradient_text(text, (0, 255, 255), (0, 100, 255))
    blue_to_purple = lambda text: gradient_text(text, (0, 150, 255), (200, 0, 255))
    
    print()
    print(f"{Colors.BRIGHT_CYAN}        ╔════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ║{Colors.RESET}                                                            {Colors.BRIGHT_CYAN}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ║{Colors.RESET}     {cyan_to_blue('██████  ██████   ██████  ██   ██ ██    ██')}              {Colors.BRIGHT_CYAN}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ║{Colors.RESET}     {cyan_to_blue('██   ██ ██   ██ ██    ██  ██ ██   ██  ██')}               {Colors.BRIGHT_CYAN}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ║{Colors.RESET}     {cyan_to_blue('██████  ██████  ██    ██   ███     ████')}                {Colors.BRIGHT_CYAN}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ║{Colors.RESET}     {cyan_to_blue('██      ██   ██ ██    ██  ██ ██     ██')}                 {Colors.BRIGHT_CYAN}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ║{Colors.RESET}     {cyan_to_blue('██      ██   ██  ██████  ██   ██    ██')}                 {Colors.BRIGHT_CYAN}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ║{Colors.RESET}                                                            {Colors.BRIGHT_CYAN}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ║{Colors.RESET}     {blue_to_purple('██████   ██████  ████████')}                              {Colors.BRIGHT_CYAN}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ║{Colors.RESET}     {blue_to_purple('██   ██ ██    ██    ██')}                                 {Colors.BRIGHT_CYAN}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ║{Colors.RESET}     {blue_to_purple('██████  ██    ██    ██')}                                 {Colors.BRIGHT_CYAN}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ║{Colors.RESET}     {blue_to_purple('██   ██ ██    ██    ██')}                                 {Colors.BRIGHT_CYAN}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ║{Colors.RESET}     {blue_to_purple('██   ██  ██████     ██')}                                 {Colors.BRIGHT_CYAN}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ║{Colors.RESET}                                                            {Colors.BRIGHT_CYAN}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}        ╚════════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()
    print(f"              {Colors.BOLD}{Colors.BRIGHT_MAGENTA}▶  IP ROTATION ARSENAL  ◀{Colors.RESET}")
    print()
    print(f"{Colors.BRIGHT_BLACK}        ┌────────────────────────────────────────────────────────────┐{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}        │{Colors.RESET}  {Colors.BRIGHT_GREEN}STATUS:{Colors.RESET} {Colors.GREEN}LOCKED & LOADED{Colors.RESET}                                   {Colors.BRIGHT_BLACK}│{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}        │{Colors.RESET}  {Colors.BRIGHT_BLUE}MODE:{Colors.RESET} {Colors.BLUE}Automatic IP Cycling{Colors.RESET}                                {Colors.BRIGHT_BLACK}│{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}        │{Colors.RESET}  {Colors.BRIGHT_YELLOW}PROVIDERS:{Colors.RESET} {Colors.YELLOW}AWS API Gateway | Google Cloud Platform{Colors.RESET}        {Colors.BRIGHT_BLACK}│{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}        └────────────────────────────────────────────────────────────┘{Colors.RESET}")
    print()


def print_menu_banner():
    """Print menu banner with gradients."""
    title = "SELECT CLOUD PROVIDER"
    title_gradient = gradient_text(title, (0, 255, 200), (150, 100, 255))
    
    indent = "        "  # 8 spaces to match other boxes
    print()
    print(f"{indent}{Colors.BRIGHT_MAGENTA}╔════════════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{indent}{Colors.BRIGHT_MAGENTA}║{Colors.RESET}                       {title_gradient}                        {Colors.BRIGHT_MAGENTA}║{Colors.RESET}")
    print(f"{indent}{Colors.BRIGHT_MAGENTA}╚════════════════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()


def print_separator(char="─", length=80, color=None):
    """Print a horizontal separator line with optional color."""
    if color:
        print(f"{color}{char * length}{Colors.RESET}")
    else:
        print(f"{Colors.BRIGHT_BLACK}{char * length}{Colors.RESET}")


def print_box(message: str, width=80):
    """Print a message in a box with gradient."""
    padding = width - len(message) - 4
    left_pad = padding // 2
    right_pad = padding - left_pad
    msg_gradient = gradient_text(message, (100, 200, 255), (200, 100, 255))
    print(f"{Colors.BRIGHT_CYAN}║{Colors.RESET} {' ' * left_pad}{msg_gradient}{' ' * right_pad} {Colors.BRIGHT_CYAN}║{Colors.RESET}")


def print_status(status: str, message: str):
    """Print a status message with formatting and colors."""
    status_config = {
        "INFO": ("►", Colors.BRIGHT_BLUE),
        "SUCCESS": ("✓", Colors.BRIGHT_GREEN),
        "ERROR": ("✗", Colors.BRIGHT_RED),
        "WAIT": ("◆", Colors.BRIGHT_YELLOW),
        "REQUEST": ("→", Colors.BRIGHT_CYAN)
    }
    symbol, color = status_config.get(status, ("•", Colors.WHITE))
    print(f"  {color}{symbol} [{status:8s}]{Colors.RESET} {message}")


def print_rotation_bar(current: int, total: int):
    """Print a rotation progress bar with gradient."""
    percentage = int((current / total) * 100)
    filled = int((current / total) * 20)
    
    # Create gradient bar
    bar_parts = []
    for i in range(20):
        if i < filled:
            # Gradient from cyan to magenta for filled portion
            ratio = i / max(filled - 1, 1) if filled > 1 else 0
            r = int(0 + (200 - 0) * ratio)
            g = int(255 - (155 * ratio))
            b = int(255)
            bar_parts.append(f"{Colors.rgb(r, g, b)}▓{Colors.RESET}")
        else:
            bar_parts.append(f"{Colors.BRIGHT_BLACK}░{Colors.RESET}")
    
    bar = ''.join(bar_parts)
    
    print()
    print(f"              {Colors.BRIGHT_BLACK}[{Colors.RESET}{bar}{Colors.BRIGHT_BLACK}]{Colors.RESET}")
    
    # Gradient percentage
    perc_text = gradient_text(f"ROTATING... {percentage}%", (0, 255, 255), (200, 100, 255))
    print(f"                  {perc_text}")
    print()
    
    if current < total:
        print(f"         {Colors.BRIGHT_CYAN}⟳  Next rotation in progress...  ⟳{Colors.RESET}")
    else:
        print(f"         {Colors.BRIGHT_GREEN}✓  All rotations complete!  ✓{Colors.RESET}")
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
    print_menu_banner()
    
    border_color = Colors.BRIGHT_BLUE
    box_width = 77
    
    def print_menu_line(content):
        """Print a menu line with proper padding."""
        vis_len = visible_length(content)
        padding = box_width - vis_len
        print(f"  {border_color}│{Colors.RESET}{content}{' ' * padding}{border_color}│{Colors.RESET}")
    
    print(f"  {border_color}┌{'═' * box_width}┐{Colors.RESET}")
    print_menu_line("")
    print_menu_line(f"    {Colors.BOLD}{Colors.BRIGHT_CYAN}[1]{Colors.RESET}  {Colors.BRIGHT_WHITE}AWS API Gateway{Colors.RESET}")
    print_menu_line(f"         {Colors.BRIGHT_BLACK}→{Colors.RESET} {Colors.CYAN}Uses Terraform-deployed API Gateway endpoints{Colors.RESET}")
    print_menu_line(f"         {Colors.BRIGHT_BLACK}→{Colors.RESET} {Colors.CYAN}Requires: terraform-aws infrastructure deployed{Colors.RESET}")
    print_menu_line(f"         {Colors.BRIGHT_BLACK}→{Colors.RESET} {Colors.CYAN}Rotates through 5 regional endpoints{Colors.RESET}")
    print_menu_line("")
    print_menu_line(f"    {Colors.BOLD}{Colors.BRIGHT_MAGENTA}[2]{Colors.RESET}  {Colors.BRIGHT_WHITE}Google Cloud Platform{Colors.RESET}")
    print_menu_line(f"         {Colors.BRIGHT_BLACK}→{Colors.RESET} {Colors.MAGENTA}Uses GCP Compute Engine with multiple regions{Colors.RESET}")
    print_menu_line(f"         {Colors.BRIGHT_BLACK}→{Colors.RESET} {Colors.MAGENTA}Requires: GCP project & gcloud authentication{Colors.RESET}")
    print_menu_line(f"         {Colors.BRIGHT_BLACK}→{Colors.RESET} {Colors.MAGENTA}Cost: Variable (based on compute usage){Colors.RESET}")
    print_menu_line("")
    print_menu_line(f"    {Colors.BOLD}{Colors.BRIGHT_YELLOW}[3]{Colors.RESET}  {Colors.BRIGHT_WHITE}View Current IPs{Colors.RESET}")
    print_menu_line(f"         {Colors.BRIGHT_BLACK}→{Colors.RESET} {Colors.YELLOW}Display available IPs without running rotation{Colors.RESET}")
    print_menu_line(f"         {Colors.BRIGHT_BLACK}→{Colors.RESET} {Colors.YELLOW}Shows IPs from deployed AWS/GCP infrastructure{Colors.RESET}")
    print_menu_line("")
    print_menu_line(f"    {Colors.BOLD}{Colors.BRIGHT_RED}[Q]{Colors.RESET}  {Colors.BRIGHT_WHITE}Quit{Colors.RESET}")
    print_menu_line("")
    print(f"  {border_color}└{'═' * box_width}┘{Colors.RESET}")
    print()
    
    while True:
        choice = input(f"  {Colors.BRIGHT_YELLOW}→{Colors.RESET} Select option {Colors.BRIGHT_BLACK}[1/2/3/Q]{Colors.RESET}: ").strip().lower()
        
        if choice in ['1', 'aws']:
            print()
            print_status("INFO", f"{Colors.BRIGHT_CYAN}Selected: AWS API Gateway{Colors.RESET}")
            return 'aws'
        elif choice in ['2', 'gcp']:
            print()
            print_status("INFO", f"{Colors.BRIGHT_MAGENTA}Selected: Google Cloud Platform{Colors.RESET}")
            return 'gcp'
        elif choice in ['3', 'view']:
            print()
            print_status("INFO", f"{Colors.BRIGHT_YELLOW}Selected: View Current IPs{Colors.RESET}")
            return 'view'
        elif choice in ['q', 'quit', 'exit']:
            print()
            print_status("INFO", "Exiting...")
            sys.exit(0)
        else:
            print(f"  {Colors.BRIGHT_RED}✗{Colors.RESET} Invalid choice. Please enter {Colors.CYAN}1{Colors.RESET}, {Colors.MAGENTA}2{Colors.RESET}, {Colors.YELLOW}3{Colors.RESET}, or {Colors.RED}Q{Colors.RESET}.")


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


def view_current_ips():
    """
    Display current available IPs from deployed infrastructure without running rotation.
    """
    print_separator()
    print()
    
    header_text = "CURRENT AVAILABLE IPs"
    header_gradient = gradient_text(header_text, (255, 200, 0), (255, 100, 200))
    print(f"        {Colors.BRIGHT_YELLOW}╔══════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"        {Colors.BRIGHT_YELLOW}║{Colors.RESET}              {header_gradient}                   {Colors.BRIGHT_YELLOW}║{Colors.RESET}")
    print(f"        {Colors.BRIGHT_YELLOW}╚══════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()
    
    # Check AWS endpoints
    print_status("INFO", f"{Colors.BRIGHT_CYAN}Checking AWS API Gateway endpoints...{Colors.RESET}")
    print()
    
    aws_endpoints = get_terraform_endpoints()
    aws_ips = []
    
    if aws_endpoints:
        print(f"  {Colors.BRIGHT_CYAN}┌─ AWS API Gateway ({len(aws_endpoints)} regions) ─────────────────────────────┐{Colors.RESET}")
        print(f"  {Colors.BRIGHT_CYAN}│{Colors.RESET}{' ' * 77}{Colors.BRIGHT_CYAN}│{Colors.RESET}")
        
        for idx, endpoint in enumerate(aws_endpoints, 1):
            try:
                # Extract region from endpoint
                region = "unknown"
                if ".execute-api." in endpoint:
                    region = endpoint.split(".execute-api.")[1].split(".")[0]
                
                # Make a quick request to get the IP
                response = requests.get(endpoint + "/ip", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    ip = extract_ip(data)
                    aws_ips.append(ip)
                    
                    # Display with gradient
                    print(f"  {Colors.BRIGHT_CYAN}│{Colors.RESET}  {Colors.BRIGHT_WHITE}[{idx}]{Colors.RESET} {Colors.CYAN}{region:15s}{Colors.RESET} {Colors.BRIGHT_BLACK}→{Colors.RESET} {Colors.BRIGHT_GREEN}{ip:50s}{Colors.RESET} {Colors.BRIGHT_CYAN}│{Colors.RESET}")
                else:
                    print(f"  {Colors.BRIGHT_CYAN}│{Colors.RESET}  {Colors.BRIGHT_WHITE}[{idx}]{Colors.RESET} {Colors.CYAN}{region:15s}{Colors.RESET} {Colors.BRIGHT_BLACK}→{Colors.RESET} {Colors.BRIGHT_RED}Failed (Status {response.status_code}){' ' * 30}{Colors.RESET} {Colors.BRIGHT_CYAN}│{Colors.RESET}")
            except Exception as e:
                print(f"  {Colors.BRIGHT_CYAN}│{Colors.RESET}  {Colors.BRIGHT_WHITE}[{idx}]{Colors.RESET} {Colors.CYAN}{region:15s}{Colors.RESET} {Colors.BRIGHT_BLACK}→{Colors.RESET} {Colors.BRIGHT_RED}Error: {str(e)[:40]:40s}{Colors.RESET} {Colors.BRIGHT_CYAN}│{Colors.RESET}")
        
        print(f"  {Colors.BRIGHT_CYAN}│{Colors.RESET}{' ' * 77}{Colors.BRIGHT_CYAN}│{Colors.RESET}")
        print(f"  {Colors.BRIGHT_CYAN}└{'─' * 77}┘{Colors.RESET}")
        print()
    else:
        print(f"  {Colors.BRIGHT_RED}✗{Colors.RESET} No AWS endpoints found. Deploy terraform-aws infrastructure first.")
        print()
    
    # Check GCP endpoints (if available)
    print_status("INFO", f"{Colors.BRIGHT_MAGENTA}Checking GCP infrastructure...{Colors.RESET}")
    print()
    
    # Check if gcloud is available
    try:
        result = subprocess.run(['gcloud', '--version'], 
                              capture_output=True, 
                              check=True, 
                              timeout=5)
        gcloud_available = True
    except:
        gcloud_available = False
    
    if not gcloud_available:
        print(f"  {Colors.BRIGHT_YELLOW}!{Colors.RESET} GCP infrastructure check skipped (gcloud CLI not available)")
        print(f"    {Colors.BRIGHT_BLACK}To enable GCP rotation:{Colors.RESET}")
        print(f"    {Colors.BRIGHT_BLACK}1.{Colors.RESET} Install gcloud CLI")
        print(f"    {Colors.BRIGHT_BLACK}2.{Colors.RESET} Deploy terraform infrastructure")
        print()
    else:
        print(f"  {Colors.BRIGHT_YELLOW}!{Colors.RESET} GCP infrastructure check available but not implemented")
        print(f"    {Colors.BRIGHT_BLACK}Use GCP rotation option to test deployed instances{Colors.RESET}")
        print()
    
    # Summary
    print_separator()
    print()
    print(f"  {Colors.BRIGHT_GREEN}✓{Colors.RESET} {Colors.BRIGHT_WHITE}Summary:{Colors.RESET}")
    print(f"    {Colors.BRIGHT_CYAN}AWS:{Colors.RESET} {Colors.CYAN}{len(aws_ips)} IPs available{Colors.RESET}")
    print()
    
    # Offer to export
    if aws_ips:
        export_choice = input(f"  {Colors.BRIGHT_YELLOW}→{Colors.RESET} Export IPs to file? {Colors.BRIGHT_BLACK}[Y/n]{Colors.RESET}: ").strip().lower()
        
        if export_choice in ['', 'y', 'yes']:
            print()
            print_status("WAIT", "Exporting IPs to current_ips.txt...")
            
            try:
                with open('current_ips.txt', 'w') as f:
                    f.write(f"# AWS API Gateway IPs - Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    for ip in aws_ips:
                        # Extract just the second IP (the rotated one)
                        if ', ' in ip:
                            rotated_ip = ip.split(', ')[1]
                            f.write(f"{rotated_ip}\n")
                        else:
                            f.write(f"{ip}\n")
                
                print_status("SUCCESS", f"{Colors.BRIGHT_GREEN}IPs exported: current_ips.txt{Colors.RESET}")
                print(f"            {Colors.BRIGHT_BLACK}Total:{Colors.RESET} {Colors.WHITE}{len(aws_ips)} IPs{Colors.RESET}")
                print()
            except Exception as e:
                print_status("ERROR", f"Failed to export: {str(e)}")
                print()
        else:
            print()
    
    print_separator()


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
        header_text = "ROTATING IP DEMONSTRATION - AWS"
        header_gradient = gradient_text(header_text, (0, 255, 255), (100, 150, 255))
        print(f"        {Colors.BRIGHT_CYAN}╔══════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"        {Colors.BRIGHT_CYAN}║{Colors.RESET}         {header_gradient}                  {Colors.BRIGHT_CYAN}║{Colors.RESET}")
        print(f"        {Colors.BRIGHT_CYAN}╚══════════════════════════════════════════════════════════╝{Colors.RESET}")
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
                
                # Display result box with colors
                box_color = Colors.BRIGHT_BLUE
                print(f"            {box_color}┌{'─' * 60}┐{Colors.RESET}")
                print(f"            {box_color}│{Colors.RESET}  {Colors.BRIGHT_YELLOW}Region:{Colors.RESET} {Colors.YELLOW}{region:<48}{Colors.RESET} {box_color}│{Colors.RESET}")
                print(f"            {box_color}│{Colors.RESET}  {Colors.BRIGHT_CYAN}IP Address:{Colors.RESET} {Colors.CYAN}{ip_address:<44}{Colors.RESET} {box_color}│{Colors.RESET}")
                print(f"            {box_color}│{Colors.RESET}  {Colors.BRIGHT_GREEN}Status Code:{Colors.RESET} {Colors.GREEN}{response.status_code:<43}{Colors.RESET} {box_color}│{Colors.RESET}")
                print(f"            {box_color}│{Colors.RESET}  {Colors.BRIGHT_MAGENTA}Response Time:{Colors.RESET} {Colors.MAGENTA}{response_time:.2f} ms{' ' * (37 - len(f'{response_time:.2f}'))}{Colors.RESET} {box_color}│{Colors.RESET}")
                print(f"            {box_color}└{'─' * 60}┘{Colors.RESET}")
                
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
        header_text = "ROTATING IP DEMONSTRATION - GCP"
        header_gradient = gradient_text(header_text, (255, 100, 200), (200, 0, 255))
        print(f"        {Colors.BRIGHT_MAGENTA}╔══════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"        {Colors.BRIGHT_MAGENTA}║{Colors.RESET}         {header_gradient}                  {Colors.BRIGHT_MAGENTA}║{Colors.RESET}")
        print(f"        {Colors.BRIGHT_MAGENTA}╚══════════════════════════════════════════════════════════╝{Colors.RESET}")
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
                
                # Display result box with colors
                box_color = Colors.BRIGHT_MAGENTA
                print(f"            {box_color}┌{'─' * 60}┐{Colors.RESET}")
                print(f"            {box_color}│{Colors.RESET}  {Colors.BRIGHT_YELLOW}Region:{Colors.RESET} {Colors.YELLOW}{region:<48}{Colors.RESET} {box_color}│{Colors.RESET}")
                print(f"            {box_color}│{Colors.RESET}  {Colors.BRIGHT_CYAN}IP Address:{Colors.RESET} {Colors.CYAN}{ip_address:<44}{Colors.RESET} {box_color}│{Colors.RESET}")
                print(f"            {box_color}│{Colors.RESET}  {Colors.BRIGHT_GREEN}Status Code:{Colors.RESET} {Colors.GREEN}{status_code:<43}{Colors.RESET} {box_color}│{Colors.RESET}")
                print(f"            {box_color}│{Colors.RESET}  {Colors.BRIGHT_MAGENTA}Response Time:{Colors.RESET} {Colors.MAGENTA}{response_time:.2f} ms{' ' * (37 - len(f'{response_time:.2f}'))}{Colors.RESET} {box_color}│{Colors.RESET}")
                print(f"            {box_color}└{'─' * 60}┘{Colors.RESET}")
                
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
    print_banner()
    
    # Display menu and get provider choice
    provider = display_menu()
    
    # Handle view option separately
    if provider == 'view':
        view_current_ips()
        return
    
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
        
        export_header = "EXPORT PROXY LIST"
        export_gradient = gradient_text(export_header, (100, 255, 100), (100, 200, 255))
        print(f"        {Colors.BRIGHT_GREEN}╔══════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"        {Colors.BRIGHT_GREEN}║{Colors.RESET}              {export_gradient}                           {Colors.BRIGHT_GREEN}║{Colors.RESET}")
        print(f"        {Colors.BRIGHT_GREEN}╚══════════════════════════════════════════════════════════╝{Colors.RESET}")
        print()
        print(f"            {Colors.BRIGHT_CYAN}Total IPs collected:{Colors.RESET} {Colors.CYAN}{len(proxy_data)}{Colors.RESET}")
        print()
        
        # Ask if user wants to export IPs to text file
        txt_choice = input(f"  {Colors.BRIGHT_YELLOW}→{Colors.RESET} Export IP list to proxies.txt? {Colors.BRIGHT_BLACK}[Y/n]{Colors.RESET}: ").strip().lower()
        
        if txt_choice in ['', 'y', 'yes']:
            print()
            print_status("WAIT", "Exporting IPs to proxies.txt...")
            if export_ips_to_txt(proxy_data, "proxies.txt"):
                print_status("SUCCESS", f"{Colors.BRIGHT_GREEN}IPs exported: proxies.txt{Colors.RESET}")
                print(f"            {Colors.BRIGHT_BLACK}Format:{Colors.RESET} {Colors.WHITE}One IP per line{Colors.RESET}")
                print(f"            {Colors.BRIGHT_BLACK}Total:{Colors.RESET} {Colors.WHITE}{len(proxy_data)} IPs{Colors.RESET}")
            print()
        else:
            print()
            print_status("INFO", "Export skipped")
            print()
    else:
        print_status("ERROR", "No proxy data collected")
        print()
    
    # Final completion message with gradient
    print_separator("═", 80, Colors.BRIGHT_MAGENTA)
    completion_text = "PROXY ROTATION COMPLETE"
    print_box(completion_text, 80)
    print_separator("═", 80, Colors.BRIGHT_MAGENTA)


if __name__ == "__main__":
    main()
