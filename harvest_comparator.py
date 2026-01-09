import os
import pandas as pd
import matplotlib.pyplot as plt
import argparse
from datetime import datetime
import re

def collect_file_info(directory):
    files_info = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
            file_type = file.split('.')[-1] if '.' in file else 'unknown'
            files_info.append({
                'path': file_path,
                'size': file_size,
                'date': file_date,
                'type': file_type
            })
    return files_info

def collect_snapshot_dates(directory):
    """Extract snapshot dates from folder names in waybackup_snapshots structure."""
    snapshot_dates = []
    
    # Look for waybackup_snapshots directory
    wayback_path = os.path.join(directory, 'waybackup_snapshots')
    if not os.path.exists(wayback_path):
        return snapshot_dates
    
    # Iterate through site directories
    for site_name in os.listdir(wayback_path):
        site_path = os.path.join(wayback_path, site_name)
        if not os.path.isdir(site_path):
            continue
        
        # Iterate through timestamp folders
        for folder_name in os.listdir(site_path):
            folder_path = os.path.join(site_path, folder_name)
            if not os.path.isdir(folder_path):
                continue
            
            # Try to parse 14-digit timestamp from folder name
            match = re.match(r'(\d{14})', folder_name)
            if match:
                timestamp_str = match.group(1)
                try:
                    snapshot_date = datetime.strptime(timestamp_str, '%Y%m%d%H%M%S')
                    snapshot_dates.append({
                        'date': snapshot_date,
                        'year': snapshot_date.year,
                        'month_day': snapshot_date.strftime('%m-%d'),
                        'site': site_name,
                        'folder': folder_name
                    })
                except ValueError:
                    pass
    
    return snapshot_dates

def analyze_directory(dir1, dir2):
    # Collect file info
    files_info_1 = collect_file_info(dir1)
    files_info_2 = collect_file_info(dir2)

    # Create DataFrames
    df1 = pd.DataFrame(files_info_1)
    df2 = pd.DataFrame(files_info_2)

    # Statistical Analysis
    for df, label in zip([df1, df2], ['Original', 'Modified']):
        print(f"\n{label} Directory Stats:")
        print(f"Total Files: {len(df)}")
        print(f"Total Size: {df['size'].sum() / (1024 * 1024):.2f} MB")
        print(df['type'].value_counts())

    # Temporal Distribution
    df1['date'] = pd.to_datetime(df1['date'])
    df2['date'] = pd.to_datetime(df2['date'])

    # Collect snapshot dates from waybackup_snapshots folders
    snapshot_dates_1 = collect_snapshot_dates(dir1)
    snapshot_dates_2 = collect_snapshot_dates(dir2)

    plt.figure(figsize=(14, 6))

    # Plot 1: Snapshot dates from folder names - Original
    if snapshot_dates_1:
        df_snap1 = pd.DataFrame(snapshot_dates_1)
        plt.subplot(1, 2, 1)
        df_snap1['date'].hist(bins=50, color='blue', alpha=0.7)
        plt.title('Limiter OFF - Harvest distribution')
        plt.xlabel('Date')
        plt.ylabel('Frequency')
    
    # Plot 2: Snapshot dates from folder names - Modified
    if snapshot_dates_2:
        df_snap2 = pd.DataFrame(snapshot_dates_2)
        plt.subplot(1, 2, 2)
        df_snap2['date'].hist(bins=50, color='orange', alpha=0.7)
        plt.title('Limiter ON - Harvest distribution')
        plt.xlabel('Date')
        plt.ylabel('Frequency')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare two harvest directories.")
    parser.add_argument("dir1", help="Path for the original harvest directory")
    parser.add_argument("dir2", help="Path for the modified harvest directory")
    
    args = parser.parse_args()
    
    analyze_directory(args.dir1, args.dir2)

