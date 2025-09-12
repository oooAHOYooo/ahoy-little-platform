#!/usr/bin/env python3
"""
Port Checker for Ahoy Indie Media
Checks which ports are available between 5001-5010
"""

import socket

def check_port(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def main():
    print("🔍 Checking port availability for Ahoy Indie Media...")
    print("Ports 5001-5010:")
    print("-" * 30)
    
    available_ports = []
    for port in range(5001, 5011):
        is_available = check_port(port)
        status = "✅ Available" if is_available else "❌ In Use"
        print(f"Port {port}: {status}")
        
        if is_available:
            available_ports.append(port)
    
    print("-" * 30)
    
    if available_ports:
        print(f"🎉 Found {len(available_ports)} available port(s): {', '.join(map(str, available_ports))}")
        print(f"💡 Recommended port: {available_ports[0]}")
    else:
        print("❌ No available ports found in range 5001-5010")
        print("💡 Try closing other applications or use a different port range")

if __name__ == "__main__":
    main()
