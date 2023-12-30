import shutil

def checkDiskUsage(path):
    # Get disk usage in percentage
    disk_usage = shutil.disk_usage(path)
    # Calculate the percentage used
    return (disk_usage.used / disk_usage.total) * 100

