import json
import csv
import os

def convert_json_to_csv(json_file_path, csv_file_path):
    """
    Convert water quality JSON data to CSV format.
    
    Args:
        json_file_path: Path to the input JSON file
        csv_file_path: Path to the output CSV file
    """
    # Read the JSON file
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    # Get all unique time points
    time_points = set()
    for parameter in data.values():
        for entry in parameter:
            time_points.add(entry['time'])
    
    time_points = sorted(time_points)
    
    # Create a dictionary to store values by time
    rows = {time: {'time': time} for time in time_points}
    
    # Populate the rows with values from each parameter
    for param_name, param_data in data.items():
        for entry in param_data:
            time = entry['time']
            value = entry['value']
            rows[time][param_name] = value
    
    # Get column names (time + all parameter names)
    columns = ['time'] + list(data.keys())
    
    # Write to CSV
    with open(csv_file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        
        for time in time_points:
            writer.writerow(rows[time])
    
    print(f"Successfully converted {json_file_path} to {csv_file_path}")
    print(f"Rows: {len(time_points)}, Columns: {len(columns)}")


if __name__ == "__main__":
    # Define file paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    json_file = os.path.join(project_root, 'frontend', 'assets', 'water_quality.json')
    csv_file = os.path.join(os.path.dirname(__file__), 'data', 'water_quality.csv')
    
    # Convert
    convert_json_to_csv(json_file, csv_file)
