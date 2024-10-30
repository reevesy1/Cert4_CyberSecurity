import platform
import os
import socket
import csv
import datetime
import psutil  # Requires 'pip install psutil'
import subprocess
import sys
import struct
import fcntl

def collect_computer_info():
    """Collects system information from the current machine."""
    computer_info = {
        "Computer Name": platform.node(),
        "IP Address": get_ip_address(),
        "MAC Address": get_mac_address(),
        "Processor Model": get_processor_model(),
        "Operating System": platform.system() + " " + platform.release(),
        "System Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Internet Status": get_internet_status(),
        "Internet Speed": get_internet_speed(),
        "Active Ports": scan_active_ports()
    }
    return computer_info

def get_ip_address():
    """Retrieves the active network IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google's DNS server
        ip_address = s.getsockname()[0]
        s.close()
        if ip_address.startswith("127."):  # Handle local IP issue
            return get_ip_via_command()
        return ip_address
    except Exception as e:
        print(f"Error fetching IP address: {e}")
        return "Unknown"

def get_ip_via_command():
    """Fallback to OS-specific commands for the real IP address."""
    try:
        result = subprocess.check_output("hostname -I", shell=True).decode().strip()
        return result.split()[0]  # Use the first IP
    except Exception as e:
        print(f"Error fetching IP address on Linux: {e}")
        return "Unknown"

def get_mac_address():
    """Retrieves the MAC address."""
    try:
        interface = b'eth0'  # Change if interface differs (e.g., wlan0)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mac = fcntl.ioctl(
            sock.fileno(),
            0x8927, # SIOCGIFHWADDR
            struct.pack('256s', interface[:15])
        )[18:24]
        return ':'.join(f'{b:02x}' for b in mac)
    except Exception as e:
        print(f"Error fetching MAC address: {e}")
        return "Unknown"

def run_command(command):
    """Executes a shell command and returns the output."""
    try:
        return subprocess.check_output(command, shell=True).decode().splitlines()[0]
    except Exception as e:
        print(f"Error running command '{command}': {e}")
        return "Unknown"

def get_processor_model():
    """Retrieves the processor model."""
    try:
        return run_command("cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d':' -f2").strip()
    except Exception as e:
        print(f"Error fetching processor model: {e}")
        return "Unknown"
    return "Unknown"

def get_internet_status():
    """Checks if the machine has internet access."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return "Connected"
    except OSError:
        return "Not Connected"

def get_internet_speed():
    """Runs an internet speed test using speedtest-cli."""
    try:
        result = subprocess.run(["speedtest-cli", "--simple"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except FileNotFoundError:
        print("speedtest-cli not found.")
    except Exception as e:
        return f"Error running speed test: {e}"

def scan_active_ports():
    """Scans for active ports on the machine."""
    active_ports = []
    for conn in psutil.net_connections():
        if conn.status == "LISTEN":
            active_ports.append(conn.laddr.port)
    return ", ".join(map(str, active_ports)) if active_ports else "None"

def save_to_csv(computer_info, csv_file="computer_info.csv"):
    """Saves the collected information to a CSV file."""
    file_exists = os.path.exists(csv_file)
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=computer_info.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(computer_info)

def main():
    """Main execution sequence."""
    computer_info = collect_computer_info()
    save_to_csv(computer_info)
    print("Information collected and saved successfully.")

if __name__ == "__main__":
    main()


