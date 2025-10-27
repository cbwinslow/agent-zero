#!/usr/bin/env python3
"""
Test script for hacking tools and OSINT libraries
Validates that all new tools are accessible
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def check_file_exists(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} (NOT FOUND)")
        return False


def check_file_content(filepath, search_text, description):
    """Check if a file contains specific text"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            if search_text in content:
                print(f"✓ {description}")
                return True
            else:
                print(f"✗ {description} (TEXT NOT FOUND)")
                return False
    except Exception as e:
        print(f"✗ {description} (ERROR: {e})")
        return False


def validate_setup():
    """Validate the hacking tools setup"""
    print("=" * 60)
    print("Hacking Tools and OSINT Libraries Validation")
    print("=" * 60)
    
    checks = []
    
    # Check tool files
    print("\n1. Checking tool files...")
    checks.append(check_file_exists(
        "python/tools/network_recon.py",
        "Network Reconnaissance Tool"
    ))
    checks.append(check_file_exists(
        "python/tools/osint_tool.py",
        "OSINT Tool"
    ))
    checks.append(check_file_exists(
        "python/tools/server_orchestration.py",
        "Server Orchestration Tool"
    ))
    checks.append(check_file_exists(
        "python/tools/web_exploit.py",
        "Web Exploitation Tool"
    ))
    
    # Check prompt documentation
    print("\n2. Checking prompt documentation...")
    checks.append(check_file_exists(
        "prompts/agent.system.tool.network_recon.md",
        "Network Recon Prompt"
    ))
    checks.append(check_file_exists(
        "prompts/agent.system.tool.osint.md",
        "OSINT Prompt"
    ))
    checks.append(check_file_exists(
        "prompts/agent.system.tool.server_orchestration.md",
        "Server Orchestration Prompt"
    ))
    checks.append(check_file_exists(
        "prompts/agent.system.tool.web_exploit.md",
        "Web Exploit Prompt"
    ))
    
    # Check documentation
    print("\n3. Checking documentation...")
    checks.append(check_file_exists(
        "docs/HACKING_TOOLS.md",
        "Hacking Tools Documentation"
    ))
    
    # Check Docker installation script
    print("\n4. Checking Docker installation script...")
    checks.append(check_file_exists(
        "docker/base/fs/ins/install_hacking_tools.sh",
        "Hacking Tools Installation Script"
    ))
    
    # Check tool classes contain proper imports and structure
    print("\n5. Checking tool class structure...")
    checks.append(check_file_content(
        "python/tools/network_recon.py",
        "class NetworkRecon(Tool):",
        "NetworkRecon class definition"
    ))
    checks.append(check_file_content(
        "python/tools/osint_tool.py",
        "class OsintTool(Tool):",
        "OsintTool class definition"
    ))
    checks.append(check_file_content(
        "python/tools/server_orchestration.py",
        "class ServerOrchestration(Tool):",
        "ServerOrchestration class definition"
    ))
    checks.append(check_file_content(
        "python/tools/web_exploit.py",
        "class WebExploit(Tool):",
        "WebExploit class definition"
    ))
    
    # Check requirements.txt
    print("\n6. Checking requirements.txt...")
    checks.append(check_file_content(
        "requirements.txt",
        "scapy==2.6.1",
        "Scapy in requirements.txt"
    ))
    checks.append(check_file_content(
        "requirements.txt",
        "shodan==1.31.0",
        "Shodan in requirements.txt"
    ))
    checks.append(check_file_content(
        "requirements.txt",
        "python-nmap==0.7.1",
        "Python-nmap in requirements.txt"
    ))
    checks.append(check_file_content(
        "requirements.txt",
        "paramiko==3.5.0",
        "Paramiko in requirements.txt (already present)"
    ))
    
    # Check Docker Dockerfile update
    print("\n7. Checking Docker configuration...")
    checks.append(check_file_content(
        "docker/base/Dockerfile",
        "install_hacking_tools.sh",
        "Hacking tools script called in Dockerfile"
    ))
    
    # Check example.env
    print("\n8. Checking environment configuration...")
    checks.append(check_file_content(
        "example.env",
        "SHODAN_API_KEY",
        "Shodan API key in example.env"
    ))
    checks.append(check_file_content(
        "example.env",
        "CENSYS_API_ID",
        "Censys API credentials in example.env"
    ))
    
    # Summary
    print("\n" + "=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("✓ All checks passed! Hacking tools are ready.")
        print("\nNext steps:")
        print("1. Run 'pip install -r requirements.txt' to install Python libraries")
        print("2. Rebuild Docker image to install system tools")
        print("3. Set API keys in .env file (optional)")
        return 0
    else:
        print(f"✗ {total - passed} checks failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(validate_setup())
