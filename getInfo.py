import platform
import os
import socket
import csv
import datetime
import psutil  # Requires 'pip install psutil'
import subprocess
import sys
import re

def collectComputerInfo():
    """Collects system information from the current machine."""
    computerInfo = {
        "Computer Name": platform.node(),
        "IP Address": getIPAddress(),
        "MAC Address": getMacAddress(),
        "Processor Model": getProcessorModel(),
        "Operating System": platform.system() + " " + platform.release(),
        "System Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Internet Speed": getInternetSpeed(),
        "Active Ports": scanActivePorts()
    }
    return computerInfo

def getIPAddress():
    """Retrieves the active network IP address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Google's DNS
            ipAddress = s.getsockname()[0]
            return ipAddress if not ipAddress.startswith("127.") else "127.0.0.1 (localhost)"
    except Exception as e:
        print(f"Error fetching IP address: {e}")
        return "Unknown"

def getMacAddress():
    """Retrieves the MAC address of the primary active network interface."""
    try:
        for interface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                    mac = next((a.address for a in addrs if a.family == psutil.AF_LINK), None)
                    return mac if mac else "Unknown"
    except Exception as e:
        print(f"Error fetching MAC address: {e}")
        return "Unknown"

def runCommand(command):
    """Executes a shell command securely and returns the output."""
    try:
        return subprocess.check_output(command, shell=True, text=True).strip()
    except Exception as e:
        print(f"Error running command '{command}': {e}")
        return "Unknown"

def getProcessorModel():
    """Retrieves the processor model based on the OS."""
    try:
        if platform.system() == "Windows":
            # Use 'wmic cpu get name' and handle output more robustly
            output = runCommand("wmic cpu get name")
            match = re.search(r'Name\s+(.+)', output, re.IGNORECASE)
            return match.group(1).strip() if match else "Unknown"
        else:
            # Linux command with refined parsing
            output = runCommand("cat /proc/cpuinfo | grep 'model name' | head -1")
            return output.split(":")[1].strip() if ":" in output else "Unknown"
    except Exception as e:
        print(f"Error fetching processor model: {e}")
        return "Unknown"

def getInternetSpeed():
    """Runs an internet speed test using speedtest-cli."""
    try:
        result = subprocess.run(["speedtest-cli", "--simple"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().splitlines()
        ping = float(lines[0].split()[1])
        download = float(lines[1].split()[1])
        upload = float(lines[2].split()[1])
        return {"ping": ping, "download": download, "upload": upload}
    except FileNotFoundError:
        return {"ping": "N/A", "download": "N/A", "upload": "N/A"}
    except Exception as e:
        return {"ping": "Unknown", "download": "Unknown", "upload": "Unknown"}

def scanActivePorts():
    """Scans for active ports on the machine."""
    activePorts = [str(conn.laddr.port) for conn in psutil.net_connections() if conn.status == "LISTEN"]
    return ";".join(activePorts) if activePorts else "None"

def logScanToCsv(computerInfo, csvFile="computer_info_log.csv"):
    """Logs the computer scan information to a CSV file and checks for significant changes."""
    fileExists = os.path.exists(csvFile)
    with open(csvFile, mode='a', newline='') as file:
        fieldnames = computerInfo.keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if not fileExists:
            writer.writeheader()
        writer.writerow(computerInfo)
        print(f"Scan recorded successfully for {computerInfo['Computer Name']}.")

    # Detect significant changes
    checkForSignificantChanges(csvFile, computerInfo)

def checkForSignificantChanges(csvFile, newInfo):
    """Checks for significant changes from the last scan in the CSV file."""
    try:
        with open(csvFile, mode='r') as file:
            rows = list(csv.DictReader(file))
            if len(rows) < 2:
                return  # Not enough data to compare yet
            
            lastScan = rows[-2]  # Compare to the previous scan

            # Threshold-based alert for internet speed changes
            speedKeys = ["ping", "download", "upload"]
            for key in speedKeys:
                try:
                    oldValue = float(lastScan["Internet Speed"][key])
                    newValue = float(newInfo["Internet Speed"][key])
                    if abs(newValue - oldValue) / oldValue >= 0.5:
                        print(f"Alert: Significant change detected in {key} speed: {oldValue} -> {newValue}")
                except (ValueError, KeyError, TypeError):
                    continue  # Handle any missing or invalid data

            # Detect other changes in hardware/OS
            for key in ["Computer Name", "IP Address", "MAC Address", "Processor Model", "Operating System"]:
                if lastScan[key] != newInfo[key]:
                    print(f"Alert: {key} changed from {lastScan[key]} to {newInfo[key]}")

    except Exception as e:
        print(f"Error checking for significant changes: {e}")

def main():
    """Main execution sequence."""
    computerInfo = collectComputerInfo()
    logScanToCsv(computerInfo)
    print("Information collected and logged successfully.")

if __name__ == "__main__":
    main()
