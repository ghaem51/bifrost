import re
def get_size_gb(file_size):
    file_size = file_size.upper()
    size_in_gb = None
    
    match = re.search(r'(\d+(\.\d+)?)([KMGT]?B)', file_size)
    if match:
        value = float(match.group(1))
        unit = match.group(3)
        
        if unit == 'B':
            size_in_gb = value / 1024 / 1024 / 1024
        elif unit == 'KB':
            size_in_gb = value / 1024 / 1024
        elif unit == 'MB':
            size_in_gb = value / 1024
        elif unit == 'GB':
            size_in_gb = value
        elif unit == 'TB':
            size_in_gb = value * 1024
        else:
            print("Invalid file size format.")
    
    return size_in_gb