#!/usr/bin/env python3
"""
File Watcher for Steensma Shop Manager
Watches the datasheets directory for new Excel files and auto-converts them to CSV
"""
import os
import time
import shutil
import zipfile
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_DIR = '/home/ubuntu/shopmgr/datasheets'
ARCHIVE_DIR = '/home/ubuntu/shopmgr/archive'
HISTORY_FILE = '/home/ubuntu/shopmgr/daily_history.json'

class DataFileHandler(FileSystemEventHandler):
    """Handle file system events for Excel files"""
    
    def extract_xlsx_to_csv(self, xlsx_path, csv_path):
        """Extract data from xlsx by parsing the raw XML (bypasses corrupt styles)"""
        try:
            with zipfile.ZipFile(xlsx_path, 'r') as z:
                # Read shared strings
                shared_strings = []
                try:
                    with z.open('xl/sharedStrings.xml') as f:
                        tree = ET.parse(f)
                        root = tree.getroot()
                        ns = {'': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                        for si in root.findall('.//t', ns):
                            shared_strings.append(si.text or '')
                except:
                    pass
                
                # Read the first worksheet
                with z.open('xl/worksheets/sheet1.xml') as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    ns = {'': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                    
                    rows_data = []
                    for row in root.findall('.//row', ns):
                        row_data = []
                        for cell in row.findall('.//c', ns):
                            cell_type = cell.get('t')
                            v = cell.find('v', ns)
                            
                            if v is not None and v.text:
                                if cell_type == 's':  # Shared string
                                    idx = int(v.text)
                                    if idx < len(shared_strings):
                                        row_data.append(shared_strings[idx])
                                    else:
                                        row_data.append('')
                                else:
                                    row_data.append(v.text)
                            else:
                                row_data.append('')
                        
                        if row_data:
                            rows_data.append(row_data)
                    
                    # Write to CSV
                    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerows(rows_data)
                    
                    return True, len(rows_data)
        except Exception as e:
            return False, str(e)
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        filename = os.path.basename(event.src_path)
        
        # Only process Excel files
        if not filename.endswith(('.xlsx', '.xls')):
            return
        
        # Check if it's one of our target files
        target_patterns = {
            'Shop Schedule': 'Scheduled Shop Jobs',
            'Scheduled Shop Jobs': 'Scheduled Shop Jobs',
            'Feb Shop Report': 'Scheduled Shop Jobs',
            'Gross Profit': 'Sales and Gross',
            'Sales and Gross': 'Sales and Gross',
            'Feb Gross Profit': 'Sales and Gross',
            'Open Back Orders': 'Open Back Orders',
            'Open ROs': 'Open Back Orders'
        }
        
        matched_pattern = None
        for pattern, output_base in target_patterns.items():
            if pattern in filename:
                matched_pattern = output_base
                break
        
        if matched_pattern:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] New file detected: {filename}")
            self.process_file(event.src_path, filename, matched_pattern)
    
    def on_modified(self, event):
        # Skip modified events to avoid duplicate processing
        pass
    
    def process_file(self, filepath, filename, output_base):
        """Process newly detected file - convert to CSV"""
        try:
            # Wait a moment for file to finish writing
            time.sleep(2)
            
            # Create archive directory with date
            today = datetime.now().strftime('%Y-%m-%d')
            archive_subdir = os.path.join(ARCHIVE_DIR, today)
            os.makedirs(archive_subdir, exist_ok=True)
            
            # Copy original to archive
            archive_path = os.path.join(archive_subdir, filename)
            shutil.copy2(filepath, archive_path)
            print(f"  ✓ Archived original to: {archive_path}")
            
            # Convert to CSV
            if filename.endswith('.xlsx'):
                csv_filename = f"{output_base} - {datetime.now().strftime('%m-%d-%y')}.csv"
                csv_path = os.path.join(WATCH_DIR, csv_filename)
                
                print(f"  → Converting to CSV: {csv_filename}")
                success, result = self.extract_xlsx_to_csv(filepath, csv_path)
                
                if success:
                    print(f"  ✓ Converted successfully! ({result} rows)")
                    print(f"  ✓ Dashboard will use: {csv_filename}")
                else:
                    print(f"  ✗ Conversion failed: {result}")
            else:
                print(f"  ℹ Skipping .xls file (only .xlsx auto-conversion supported)")
                print(f"  ℹ Please save as .xlsx or manually convert to CSV")
            
            print()
            
        except Exception as e:
            print(f"  ✗ Error processing file: {e}")
            print()

def main():
    """Main file watcher loop"""
    print("=" * 70)
    print("Steensma Shop Manager - Auto Excel-to-CSV Converter")
    print("=" * 70)
    print(f"Watching directory: {WATCH_DIR}")
    print(f"Archive directory: {ARCHIVE_DIR}")
    print()
    print("📥 Drop your Excel files (.xlsx) into the datasheets folder")
    print("⚙️  They will be automatically converted to CSV")
    print("🎯 Supported files:")
    print("   • Shop Schedule / Feb Shop Report → Scheduled Shop Jobs CSV")
    print("   • Gross Profit / Feb Gross Profit → Sales and Gross CSV")
    print("   • Open Back Orders / Open ROs → Open Back Orders CSV")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 70)
    print()
    
    # Create directories if they don't exist
    os.makedirs(WATCH_DIR, exist_ok=True)
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    # Set up file system observer
    event_handler = DataFileHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=False)
    observer.start()
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 👀 Watching for new files...")
    print()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping file watcher...")
        observer.stop()
    
    observer.join()
    print("✓ File watcher stopped.")
    print()

if __name__ == '__main__':
    main()
