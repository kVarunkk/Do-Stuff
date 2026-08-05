import json
import re
import sys

def parse_logs(log_file_path):
    output_data = {}
    
    # Regex to match ERROR/CRITICAL and extract parts
    # Format: YYYY-MM-DD HH:MM:SS LEVEL CODE Module:Name Message
    log_pattern = re.compile(r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (?:ERROR|CRITICAL) (?P<code>\S+) Module:(?P<module>\S+) (?P<message>.*)')

    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                if 'ERROR' in line or 'CRITICAL' in line:
                    match = log_pattern.search(line)
                    if match:
                        data = match.groupdict()
                        code = data.pop('code')
                        if code not in output_data:
                            output_data[code] = []
                        output_data[code].append(data)
    except FileNotFoundError:
        print(f"Error: File {log_file_path} not found.")
        sys.exit(1)

    print(json.dumps(output_data, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_logs.py <log_file_path>")
        sys.exit(1)
    parse_logs(sys.argv[1])
