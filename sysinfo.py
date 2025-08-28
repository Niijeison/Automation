import shutil

total, used, free = shutil.disk_usage("/")
print(f"Disk Total: {total // (2**30)} GB")
print(f"Disk Used: {used // (2**30)} GB")
print(f"Disk Free: {free // (2**30)} GB")

with open("/proc/uptime", "r") as f:
    uptime_seconds = float(f.readline().split()[0])
    uptime_hours = uptime_seconds / 3600
    print(f"System Uptime: {uptime_hours:.2f} hours")

import os

users = os.popen("who").read()
print("Logged-in Users:\n", users)

import psutil  # install with: pip3 install psutil

print(f"CPU Usage: {psutil.cpu_percent()}%")
print(f"Memory Usage: {psutil.virtual_memory().percent}%")
