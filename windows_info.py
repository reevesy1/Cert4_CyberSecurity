import platform
import socket
import subprocess
import csv
import datetime
import speedtest
import os
import psutil

def collect_computer_info():
    """Collects system information for Windows."""
    computer_info = {
        "Computer Name": platform.node(),
        "IP Address": get_ip_address(),
        "MAC Address": get_mac_address(),
        "Processor Model": platform.processor(),
        "Operating System": platform.system() + " " + platform.release(),
        "System Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Internet Status": get_internet_status(),
        "Internet Speed": run_speedtest(),
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
        return ip_address
    except Exception as e:
        print(f"Error fetching IP address: {e}")
        return "Unknown"

def get_mac_address():
    """Retrieves the MAC address."""
    try:
        result = subprocess.check_output("ipconfig /all", shell=True).decode()
        for line in result.splitlines():
            if "Physical Address" in line or "MAC" in line:
                return line.split(":")[-1].strip()
    except Exception as e:
        print(f"Error fetching MAC address: {e}")
        return "Unknown"

def scan_active_ports():
    """Scans for active ports using netstat."""
    try:
        result = subprocess.check_output("netstat -an", shell=True).decode()
        ports = set()
        for line in result.splitlines():
            if "LISTENING" in line:
                port = line.split()[1].split(':')[-1]
                ports.add(port)
        return ", ".join(ports) if ports else "None"
    except Exception as e:
        print(f"Error scanning ports: {e}")
        return "Unknown"

def get_internet_status():
    """Checks if the machine has internet access."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return "Connected"
    except OSError:
        return "Not Connected"

def run_speedtest():
    """Runs a speed test and returns download/upload speeds."""
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download_speed = st.download() / 1_000_000  # Convert to Mbps
        upload_speed = st.upload() / 1_000_000  # Convert to Mbps
        return f"Download: {download_speed:.2f} Mbps, Upload: {upload_speed:.2f} Mbps"
    except Exception as e:
        return f"Error running speedtest: {e}"

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
