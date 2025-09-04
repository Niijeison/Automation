#!/usr/bin/env python3
import platform
import socket
import psutil
import datetime
import os
import subprocess

REPORT_FILE = "/var/log/system_inventory.txt"

def collect_inventory():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report = []
    report.append(f"System Inventory Report - {now}")
    report.append("=" * 60)

    # OS and Kernel
    report.append("\n[OS INFORMATION]")
    report.append(f"OS        : {platform.system()} {platform.release()}")
    report.append(f"Kernel    : {platform.version()}")
    report.append(f"Arch      : {platform.machine()}")
    report.append(f"Platform  : {platform.platform()}")

    # Hostname and IP
    report.append("\n[HOSTNAME & NETWORK]")
    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        ip = "N/A"
    report.append(f"Hostname  : {hostname}")
    report.append(f"IP Addr   : {ip}")

    # Network interfaces
    report.append("\n[NETWORK INTERFACES]")
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET:
                report.append(f"{iface:10} IP: {addr.address} | Netmask: {addr.netmask}")

    # CPU and Memory
    report.append("\n[CPU & MEMORY]")
    report.append(f"CPU Cores : {psutil.cpu_count(logical=True)}")
    report.append(f"CPU Usage : {psutil.cpu_percent(interval=1)}%")
    mem = psutil.virtual_memory()
    report.append(f"Memory    : {mem.total // (1024**3)} GB total, {mem.percent}% used")

    # Disk usage
    report.append("\n[DISK USAGE]")
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            report.append(f"{part.mountpoint:10} {usage.total // (1024**3)} GB total, {usage.percent}% used")
        except PermissionError:
            continue

    # Running processes (top 5 by memory usage)
    report.append("\n[TOP 5 PROCESSES BY MEMORY]")
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'memory_percent']):
        try:
            processes.append(p.info)
        except psutil.NoSuchProcess:
            continue
    top5 = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:5]
    for p in top5:
        report.append(f"PID {p['pid']:<6} {p['name']:<20} {p['memory_percent']:.2f}% memory")

    # Installed packages (Debian/Ubuntu only)
    report.append("\n[INSTALLED PACKAGES COUNT]")
    try:
        result = subprocess.run(["dpkg", "-l"], capture_output=True, text=True)
        pkg_count = len(result.stdout.strip().split("\n")) - 5
        report.append(f"Total installed packages: {pkg_count}")
    except FileNotFoundError:
        report.append("dpkg not available (non-Debian system)")

    return "\n".join(report)

def save_report(data):
    with open(REPORT_FILE, "w") as f:
        f.write(data)

if __name__ == "__main__":
    inventory = collect_inventory()
    save_report(inventory)
    print(inventory)
    print(f"\n[+] Report saved to {REPORT_FILE}")

