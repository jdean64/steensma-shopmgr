"""
Steensma Shop Manager Dashboard
Processes daily shop schedules, parts, and mechanic metrics
"""
import os
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Configuration
DATASHEETS_DIR = os.path.join(os.path.dirname(__file__), 'datasheets')
ARCHIVE_DIR = os.path.join(os.path.dirname(__file__), 'archive')

def get_latest_file(patterns):
    """Get the most recent file matching one or more patterns"""
    if isinstance(patterns, str):
        patterns = [patterns]
    patterns = [p.lower() for p in patterns]
    files = [
        f for f in os.listdir(DATASHEETS_DIR)
        if any(p in f.lower() for p in patterns)
    ]
    if not files:
        return None
    latest = max(files, key=lambda f: os.path.getmtime(os.path.join(DATASHEETS_DIR, f)))
    return os.path.join(DATASHEETS_DIR, latest)

def read_excel_safe(filepath, **kwargs):
    """Read Excel files with engine fallbacks for corrupted styles"""
    try:
        if filepath.lower().endswith('.xlsx'):
            return pd.read_excel(filepath, engine='openpyxl', **kwargs)
        return pd.read_excel(filepath, engine='xlrd', **kwargs)
    except Exception as e:
        try:
            return pd.read_excel(filepath, engine='calamine', **kwargs)
        except Exception as e2:
            print(f"Error reading Excel file {os.path.basename(filepath)}: {e}")
            print(f"Fallback to calamine failed: {e2}")
            raise

def parse_shop_schedule(filepath):
    """
    Parse Shop Schedule file (supports both text and Excel formats)
    Extract Today's Schedule, Tomorrow's Schedule, and Fit-Ins
    """
    try:
        # Check if it's a text file
        if filepath.endswith('.txt'):
            with open(filepath, 'r') as f:
                content = f.read()
            
            schedule_data = {
                'today': [],
                'tomorrow': [],
                'fit_ins': []
            }
            
            # Get today and tomorrow date strings
            # Skip weekends - treat Monday as "today" if it's Sat/Sun
            now = datetime.now()
            if now.weekday() == 5:  # Saturday
                today = now + timedelta(days=2)  # Monday
                tomorrow = now + timedelta(days=3)  # Tuesday
            elif now.weekday() == 6:  # Sunday
                today = now + timedelta(days=1)  # Monday
                tomorrow = now + timedelta(days=2)  # Tuesday
            else:
                today = now
                tomorrow = now + timedelta(days=1)
            
            today_str = today.strftime('%-m/%-d/%Y')  # e.g., 1/15/2026
            tomorrow_str = tomorrow.strftime('%-m/%-d/%Y')

            
            lines = content.split('\n')
            current_mechanic = None
            in_fit_in_section = False
            
            for line in lines:
                line = line.strip()
                
                # Check for mechanic name (with or without 'p' prefix or 'b' prefix)
                if line.startswith('bDerek Snyder') or line.startswith('pDerek Snyder'):
                    current_mechanic = 'Derek Snyder'
                    in_fit_in_section = False
                elif line.startswith('bChris Deman') or line.startswith('pChris Deman'):
                    current_mechanic = 'Chris Deman'
                    in_fit_in_section = False
                elif line.startswith('bBrandon Wallace') or line.startswith('pBrandon Wallace'):
                    current_mechanic = 'Brandon Wallace'
                    in_fit_in_section = False
                elif line == 'FIT IN WORK' or line.startswith('.pFIT IN') or 'Fit-In' in line:
                    in_fit_in_section = True
                    current_mechanic = 'Fit-In'
                    continue
                elif line.startswith('.pHouse Account') or line.startswith('pHouse Account'):
                    in_fit_in_section = True
                    current_mechanic = 'House Account'
                    continue
                
                # Parse job lines (contain comma-separated data)
                if ',' in line and not line.startswith('Invoice,') and not line.startswith('Mechanics'):
                    parts = line.split(',')
                    if len(parts) >= 9:  # Must have all columns
                        invoice = parts[0]
                        customer = parts[1]
                        model = parts[2]
                        description = parts[3]
                        estimated_time = parts[4]
                        start_time = parts[5]
                        end_time = parts[6]
                        priority = parts[7]
                        status = parts[8]
                        
                        # Skip if no invoice number (likely not a job line)
                        if not invoice or not invoice.isdigit():
                            continue
                        
                        job_data = {
                            'customer': customer,
                            'job': f"{model} - {description[:50]}..." if len(description) > 50 else f"{model} - {description}",
                            'mechanic': current_mechanic or 'Unassigned',
                            'time': start_time,
                            'status': status
                        }
                        
                        # Only include if it's a fit-in or house account job
                        if in_fit_in_section and current_mechanic in ['Fit-In', 'House Account']:
                            schedule_data['fit_ins'].append(job_data)
                        # Skip regular mechanic jobs (Derek, Chris, Brandon)
            
            return schedule_data
        
        else:
            # Excel or CSV format
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
            elif filepath.endswith('.xlsx'):
                df = pd.read_excel(filepath, engine='openpyxl')
            else:
                df = pd.read_excel(filepath, engine='xlrd')
            
            today = datetime.now().date()
            tomorrow = pd.Timestamp(today) + pd.Timedelta(days=1)
            
            schedule_data = {
                'today': [],
                'tomorrow': [],
                'fit_ins': []
            }
            
            # Find rows with ScheduledStartTime column
            if 'ScheduledStartTime' in df.columns:
                # Parse dates - handle various formats
                df['ScheduledStartTime'] = pd.to_datetime(df['ScheduledStartTime'], errors='coerce')
                
                # Today's schedule
                today_df = df[df['ScheduledStartTime'].dt.date == today]
                for _, row in today_df.iterrows():
                    schedule_data['today'].append({
                        'customer': str(row.get('Customer', '')),
                        'job': f"{row.get('Model', '')} - {row.get('description', '')}"[:80],
                        'mechanic': str(row.get('Mechanic', '')),
                        'time': row['ScheduledStartTime'].strftime('%I:%M %p') if pd.notna(row['ScheduledStartTime']) else ''
                    })
                
                # Tomorrow's schedule
                tomorrow_df = df[df['ScheduledStartTime'].dt.date == tomorrow.date()]
                for _, row in tomorrow_df.iterrows():
                    schedule_data['tomorrow'].append({
                        'customer': str(row.get('Customer', '')),
                        'job': f"{row.get('Model', '')} - {row.get('description', '')}"[:80],
                        'mechanic': str(row.get('Mechanic', '')),
                        'time': row['ScheduledStartTime'].strftime('%I:%M %p') if pd.notna(row['ScheduledStartTime']) else ''
                    })
                
                # If no today/tomorrow data, show the most recent scheduled jobs
                if len(schedule_data['today']) == 0 and len(schedule_data['tomorrow']) == 0:
                    recent_df = df[pd.notna(df['ScheduledStartTime'])].sort_values('ScheduledStartTime', ascending=False).head(15)
                    for _, row in recent_df.iterrows():
                        schedule_data['today'].append({
                            'customer': str(row.get('Customer', '')),
                            'job': f"{row.get('Model', '')} - {row.get('description', '')}"[:80],
                            'mechanic': str(row.get('Mechanic', '')),
                            'time': row['ScheduledStartTime'].strftime('%m/%d %I:%M %p') if pd.notna(row['ScheduledStartTime']) else ''
                        })
            
            # Find Fit-Ins and House Account jobs (Mechanic column contains "Fit-In" or "House Account")
            if 'Mechanic' in df.columns:
                fit_in_df = df[df['Mechanic'].astype(str).str.contains('Fit-In|House Account', case=False, na=False)]
                for _, row in fit_in_df.iterrows():
                    schedule_data['fit_ins'].append({
                        'customer': str(row.get('Customer', '')),
                        'job': f"{row.get('Model', '')} - {row.get('description', '')}"[:80],
                        'notes': str(row.get('Status', ''))
                    })
            
            return schedule_data
    
    except Exception as e:
        print(f"Error parsing shop schedule: {e}")
        import traceback
        traceback.print_exc()
        return {'today': [], 'tomorrow': [], 'fit_ins': [], 'error': str(e)}

def parse_open_back_orders(filepath):
    """
    Parse Open Back Orders file
    Extract parts where Status is 'Back-Ordered' 
    """
    try:
        # Read file based on extension
        if filepath.endswith('.txt'):
            # Parse text format
            with open(filepath, 'r') as f:
                content = f.read()
            
            parts_received = []
            lines = content.split('\n')
            
            # Look for lines with "Back-Ordered"
            for line in lines:
                line = line.strip()
                if not line or ',' not in line:
                    continue
                
                # Check for back-ordered/on order status
                if 'Back-Ordered' in line:
                    parts = line.split(',')
                    if len(parts) >= 3:
                        # Format: Customer,Phone,Part Number,...,Status,...
                        customer = parts[0].strip() if parts[0] else ''
                        part_number = parts[2].strip() if len(parts) > 2 else ''
                        status = 'Back-Ordered'   # Only Back-Ordered items
                        
                        if part_number and part_number != 'Part Number':  # Skip header
                            parts_received.append({
                                'part_number': part_number,
                                'customer': customer if customer and customer != 'Customer' else 'N/A',
                                'status': status
                            })
            
            return parts_received
        
        elif filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath, engine='xlrd')
        
        parts_received = []
        
        # The header is at row 4 (index 4) for Excel files
        # Customer is column 1, Part Number is column 9, Status is column 17
        # Re-read with proper header (skip for CSV as it has headers already)
        if not filepath.endswith('.csv'):
            df = pd.read_excel(filepath, engine='xlrd', header=4)
        
        # Clean up column names
        df.columns = [str(col).strip() if pd.notna(col) else f'Col_{i}' for i, col in enumerate(df.columns)]
        
        # Find columns by name or position
        customer_col = 'Customer' if 'Customer' in df.columns else df.columns[1]
        part_col = df.columns[9]  # Part number is at column index 9
        status_col = 'Status' if 'Status' in df.columns else df.columns[17]
        
        # Filter for Back-Ordered only
        for _, row in df.iterrows():
            status = str(row[status_col]).strip() if pd.notna(row[status_col]) else ''
            part_number = str(row[part_col]).strip() if pd.notna(row[part_col]) else ''
            customer = str(row[customer_col]).strip() if pd.notna(row[customer_col]) else ''
            
            # Check if status contains Back-Ordered or On Order
            if ('back-ordered' in status.lower()) and part_number and part_number != 'nan':
                parts_received.append({
                    'part_number': part_number,
                    'customer': customer if customer and customer != 'nan' else 'N/A',
                    'status': status
                })
        
        return parts_received
    
    except Exception as e:
        print(f"Error parsing open back orders: {e}")
        import traceback
        traceback.print_exc()
        return []

def parse_backorders_over_5(filepath):
    """
    Parse Open Back Orders file for items 5+ days old
    Extract customer contact info, part number, age, and status
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        backorders = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or ',' not in line:
                continue
            
            # Skip header lines
            if 'Customer' in line or 'Steensma' in line or 'Invoice' in line:
                continue
            if 'Repair Orders' in line or 'Open Back Orders' in line:
                continue
            
            # Check for back-ordered/on order status
            if 'Back-Ordered' in line  in line:
                parts = line.split(',')
                
                # Format: Customer,Phone,Part Number,Type,PP,Age,Ordered,Status,...
                if len(parts) >= 9:
                    customer = parts[0].strip()
                    phone = parts[1].strip()
                    part_number = parts[2].strip()
                    age_str = parts[6].strip()  # Age is column 6 (0-indexed)
                    status = parts[8].strip()   # Status is column 8 (0-indexed)
                    
                    # Try to parse age as integer
                    try:
                        age = int(age_str) if age_str else 0
                    except ValueError:
                        age = 0
                    
                    # Only include items 5+ days old
                    if age >= 5 and part_number:
                        # Use previous row's customer/phone if current row is blank
                        if not customer and backorders:
                            customer = backorders[-1]['customer']
                            phone = backorders[-1]['phone']
                        
                        backorders.append({
                            'customer': customer if customer else 'N/A',
                            'phone': phone if phone else 'N/A',
                            'part_number': part_number,
                            'age': age,
                            'status': status,
                            'priority': 'critical' if age >= 30 else 'high' if age >= 15 else 'medium' if age >= 10 else 'normal'
                        })
        
        # Sort by age descending (oldest first)
        backorders.sort(key=lambda x: x['age'], reverse=True)
        
        return backorders
    
    except Exception as e:
        print(f"Error parsing backorders over 5: {e}")
        import traceback
        traceback.print_exc()
        return []

def parse_po_over_30(filepath):
    """
    Parse PO Over 30 file
    Extract purchase orders 30+ days old grouped by vendor
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        po_data = []
        lines = content.split('\n')
        current_vendor = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip header lines
            if 'Purchase Order' in line or 'Steensma' in line or 'Vendor Name' in line:
                continue
            if 'PO Number' in line or 'Ordered' in line:
                continue
            
            # Check if this is a vendor name line (no commas, or minimal structure)
            parts = line.split(',')
            
            # Vendor lines typically have few columns or are standalone names
            if len(parts) <= 2 and not line[0].isdigit():
                # This is likely a vendor name
                current_vendor = parts[0].strip()
                continue
            
            # PO lines have format: PO Number,Age,Status,Since,Return,Items,Pieces,Total,...
            if len(parts) >= 8 and current_vendor:
                po_number = parts[0].strip()
                age_str = parts[1].strip()
                status = parts[2].strip()
                since = parts[3].strip()
                items = parts[5].strip()
                total = parts[7].strip()
                
                # Try to parse age
                try:
                    age = int(age_str) if age_str else 0
                except ValueError:
                    continue
                
                # Only include POs 30+ days old
                if age >= 30 and po_number:
                    po_data.append({
                        'vendor': current_vendor,
                        'po_number': po_number,
                        'age': age,
                        'status': status,
                        'since': since,
                        'items': items,
                        'total': total,
                        'priority': 'critical' if age >= 90 else 'high' if age >= 60 else 'medium'
                    })
        
        # Sort by age descending (oldest first)
        po_data.sort(key=lambda x: x['age'], reverse=True)
        
        return po_data
    
    except Exception as e:
        print(f"Error parsing PO over 30: {e}")
        import traceback
        traceback.print_exc()
        return []

def parse_no_bins(filepath):
    """
    Parse No Bins file
    Extract parts that need to be binned (no bin location assigned)
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        no_bins = []
        lines = content.split('\n')
        
        # Skip header lines and footer
        for line in lines:
            line = line.strip()
            
            # Skip empty lines, headers, and footer
            if not line or ',' not in line:
                continue
            if 'Steensma' in line or 'Bin Census' in line or 'Zone' in line:
                continue
            if 'Page' in line or ' of ' in line:
                continue
            
            # Parse CSV format: ,Line Code,Part Number,O/C,Description,Class,Available
            parts = line.split(',')
            
            # Must have at least 7 columns and start with empty bin (first column empty)
            if len(parts) >= 7 and parts[0].strip() == '':
                line_code = parts[1].strip()
                part_number = parts[2].strip()
                description = parts[4].strip()
                available = parts[6].strip()
                
                # Skip if this is the header row
                if part_number and part_number != 'Part Number':
                    no_bins.append({
                        'line_code': line_code,
                        'part_number': part_number,
                        'description': description,
                        'available': available
                    })
        
        return no_bins
    
    except Exception as e:
        print(f"Error parsing no bins file: {e}")
        import traceback
        traceback.print_exc()
        return []

def parse_gross_profit_mechanic(filepath):
    """
    Parse Gross Profit Mechanic file
    Extract efficiency and labor sales for Dennis Smurr, Jake Glas, and Ray Page
    
    Supports both Excel and text file formats
    """
    try:
        # Check if it's a text file
        if filepath.endswith('.txt'):
            with open(filepath, 'r') as f:
                content = f.read()
            
            mechanic_metrics = []
            
            # Parse text format - look for summary lines with mechanic names
            lines = content.split('\n')
            
            import re
            
            for line in lines:
                # Match mechanic summary lines - they start with 'b' or 'p' and mechanic name
                if (line.startswith('bDerek Snyder,') or line.startswith('pDerek Snyder,')) and len(line) > 50:
                    # Use regex to extract dollar amounts: $4,272.09
                    # The pattern is: Parts Sales, Parts COGS, Parts %, Labor Sales, Labor COGS, Labor %, etc.
                    dollar_amounts = re.findall(r'\$[\d,]+\.?\d*', line)
                    if len(dollar_amounts) >= 3:
                        # Labor Sales is the 3rd dollar amount (index 2)
                        labor_sales = dollar_amounts[2].replace('$', '').replace(',', '')
                        try:
                            labor_sales = float(labor_sales)
                        except:
                            labor_sales = 0
                        
                        mechanic_metrics.append({
                            'name': 'Derek Snyder',
                            'efficiency': 0,  # Will update from Hours Worked line
                            'labor_sales': labor_sales
                        })
                
                elif (line.startswith('bChris Deman,') or line.startswith('pChris Deman,') or 
                      line.startswith('pCHRIS DEMANN,') or line.startswith('bCHRIS DEMANN,')) and len(line) > 50:
                    dollar_amounts = re.findall(r'\$[\d,]+\.?\d*', line)
                    if len(dollar_amounts) >= 3:
                        labor_sales = dollar_amounts[2].replace('$', '').replace(',', '')
                        try:
                            labor_sales = float(labor_sales)
                        except:
                            labor_sales = 0
                        
                        mechanic_metrics.append({
                            'name': 'Chris Deman',
                            'efficiency': 0,
                            'labor_sales': labor_sales
                        })
                
                elif (line.startswith('bBrandon Wallace,') or line.startswith('pBrandon Wallace,')) and len(line) > 50:
                    dollar_amounts = re.findall(r'\$[\d,]+\.?\d*', line)
                    if len(dollar_amounts) >= 3:
                        labor_sales = dollar_amounts[2].replace('$', '').replace(',', '')
                        try:
                            labor_sales = float(labor_sales)
                        except:
                            labor_sales = 0
                        
                        mechanic_metrics.append({
                            'name': 'Brandon Wallace',
                            'efficiency': 0,
                            'labor_sales': labor_sales
                        })
                
                # Look for efficiency data - "Hours Worked:,61:14,71%,46%"
                # Using the first percentage (index 2) not the second (index 3)
                if 'Hours Worked:' in line:
                    parts = line.split(',')
                    if len(parts) >= 3:
                        try:
                            efficiency_str = parts[2].replace('%', '').strip()
                            efficiency = float(efficiency_str)
                            
                            # Update the last added mechanic
                            if mechanic_metrics:
                                mechanic_metrics[-1]['efficiency'] = efficiency
                        except:
                            pass
            
            # Calculate overall efficiency
            efficiencies = [m['efficiency'] for m in mechanic_metrics if m['efficiency'] > 0]
            overall_efficiency = sum(efficiencies) / len(efficiencies) if efficiencies else 0
            
            return {
                'mechanics': mechanic_metrics,
                'overall_efficiency': overall_efficiency
            }
        
        # If not a text file, try Excel or CSV parsing
        else:
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
                
                # Parse CSV: aggregate by mechanic name
                mechanic_metrics = []
                mechanic_names = ['Derek Snyder', 'Chris Deman', 'Brandon Wallace']
                
                for mechanic_name in mechanic_names:
                    # Filter rows for this mechanic (with 'p' prefix, case-insensitive)
                    mechanic_rows = df[df['Mechanic'].str.contains(mechanic_name, case=False, na=False, regex=False)]
                    
                    if not mechanic_rows.empty:
                        # Sum up Labor Sales
                        labor_sales = 0
                        for _, row in mechanic_rows.iterrows():
                            labor_val = str(row.get('Labor Sales', '0'))
                            # Clean currency formatting
                            labor_val = labor_val.replace('$', '').replace(',', '').replace('(', '-').replace(')', '')
                            try:
                                labor_sales += float(labor_val)
                            except:
                                pass
                        
                        # Calculate efficiency from Time Billed / Time Actual
                        time_billed_total = 0
                        time_actual_total = 0
                        for _, row in mechanic_rows.iterrows():
                            tb = str(row.get('Time Billed', '0:00'))
                            ta = str(row.get('Time Actual', '0:00'))
                            # Convert HH:MM to minutes
                            try:
                                if ':' in tb:
                                    h, m = tb.split(':')
                                    time_billed_total += int(h) * 60 + int(m)
                                if ':' in ta:
                                    h, m = ta.split(':')
                                    time_actual_total += int(h) * 60 + int(m)
                            except:
                                pass
                        
                        efficiency = 0
                        if time_actual_total > 0:
                            efficiency = (time_billed_total / time_actual_total) * 100
                        
                        mechanic_metrics.append({
                            'name': mechanic_name,
                            'efficiency': round(efficiency, 1),
                            'labor_sales': round(labor_sales, 2)
                        })
                
            else:
                df = pd.read_excel(filepath, engine='xlrd')
            
            mechanics = {
                'Derek Snyder': {'efficiency_cell': 'G120', 'labor_cell': 'O119'},
                'Chris Deman': {'efficiency_cell': 'G189', 'labor_cell': 'O188'},
                'Brandon Wallace': {'efficiency_cell': 'G233', 'labor_cell': 'O232'}
            }
            
            mechanic_metrics = []
            
            for mechanic_name, cells in mechanics.items():
                try:
                    # Extract cell references (e.g., G120 -> column G, row 120)
                    eff_col = cells['efficiency_cell'][0]
                    eff_row = int(cells['efficiency_cell'][1:]) - 1  # Zero-indexed
                    
                    labor_col = cells['labor_cell'][0]
                    labor_row = int(cells['labor_cell'][1:]) - 1
                    
                    # Convert column letter to index (A=0, B=1, etc.)
                    eff_col_idx = ord(eff_col) - ord('A')
                    labor_col_idx = ord(labor_col) - ord('A')
                    
                    # Extract values
                    efficiency = df.iloc[eff_row, eff_col_idx] if eff_row < len(df) else None
                    labor_sales = df.iloc[labor_row, labor_col_idx] if labor_row < len(df) else None
                    
                    # Clean up the values
                    if pd.notna(efficiency):
                        if isinstance(efficiency, str) and '%' in str(efficiency):
                            efficiency = efficiency.replace('%', '')
                        try:
                            efficiency = float(efficiency)
                        except:
                            pass
                    
                    if pd.notna(labor_sales):
                        if isinstance(labor_sales, str):
                            labor_sales = labor_sales.replace('$', '').replace(',', '')
                        try:
                            labor_sales = float(labor_sales)
                        except:
                            pass
                    
                    mechanic_metrics.append({
                        'name': mechanic_name,
                        'efficiency': efficiency if pd.notna(efficiency) else 0,
                        'labor_sales': labor_sales if pd.notna(labor_sales) else 0
                    })
                
                except Exception as e:
                    print(f"Error parsing metrics for {mechanic_name}: {e}")
                    mechanic_metrics.append({
                        'name': mechanic_name,
                        'efficiency': 0,
                        'labor_sales': 0
                    })
            
            # Calculate overall efficiency
            efficiencies = [m['efficiency'] for m in mechanic_metrics if isinstance(m['efficiency'], (int, float))]
            overall_efficiency = sum(efficiencies) / len(efficiencies) if efficiencies else 0
            
            return {
                'mechanics': mechanic_metrics,
                'overall_efficiency': overall_efficiency
            }
    
    except Exception as e:
        print(f"Error parsing gross profit mechanic: {e}")
        import traceback
        traceback.print_exc()
        return {'mechanics': [], 'overall_efficiency': 0}


def find_quarterly_sales_file():
    """Find the most recent Site lead Statement text file"""
    txt_files = [
        os.path.join(DATASHEETS_DIR, f)
        for f in os.listdir(DATASHEETS_DIR)
        if f.lower().endswith('.txt')
    ]
    
    if not txt_files:
        return None
    
    # Check most recently modified files first (faster)
    txt_files_sorted = sorted(txt_files, key=os.path.getmtime, reverse=True)
    
    # Check all files
    for path in txt_files_sorted[:5]:
        try:
            with open(path, 'r') as f:
                head = ''.join([next(f) for _ in range(3)])
            if 'Site lead Statement' in head:
                return path
        except Exception:
            continue
    
    return None


def parse_quarterly_sales(filepath):
    """
    Parse Site lead Statement file for quarterly sales metrics
    Extract New Equipment Sales, Parts Sales, and Labor Sales (Month and YTD 2026)
    """
    def parse_money(value):
        if value is None:
            return 0.0
        s = str(value).strip()
        if not s:
            return 0.0
        s = s.replace('$', '').replace(',', '')
        if s.startswith('(') and s.endswith(')'):
            s = '-' + s[1:-1]
        try:
            return float(s)
        except:
            return 0.0
    
    try:
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
        
        new_equipment = {'month': 0.0, 'ytd': 0.0, 'py_month': 0.0, 'py_ytd': 0.0}
        parts_sales = {'month': 0.0, 'ytd': 0.0, 'py_month': 0.0, 'py_ytd': 0.0}
        labor_sales = {'month': 0.0, 'ytd': 0.0, 'py_month': 0.0, 'py_ytd': 0.0}
        
        import re
        
        def next_values_after(label):
            for idx, line in enumerate(lines):
                if line.upper() == label:
                    # Find next non-empty line with numeric values
                    for j in range(idx + 1, min(idx + 4, len(lines))):
                        if lines[j] and ',' in lines[j]:
                            # Extract money-like values with commas/decimals
                            # Split by comma and return values that look like money
                            return re.findall(r'\(?\d{1,3}(?:,\d{3})*\.\d{2}\)?', lines[j])
            return []
        
        new_vals = next_values_after('NEW EQUIPMENT SALES')
        parts_vals = next_values_after('PARTS SALES')
        labor_vals = next_values_after('SERVICE LABOR SALES')
        
        if len(new_vals) >= 4:
            new_equipment['month'] = parse_money(new_vals[0])
            new_equipment['ytd'] = parse_money(new_vals[1])
            new_equipment['py_month'] = parse_money(new_vals[2])
            new_equipment['py_ytd'] = parse_money(new_vals[3])
        
        if len(parts_vals) >= 4:
            parts_sales['month'] = parse_money(parts_vals[0])
            parts_sales['ytd'] = parse_money(parts_vals[1])
            parts_sales['py_month'] = parse_money(parts_vals[2])
            parts_sales['py_ytd'] = parse_money(parts_vals[3])
        
        if len(labor_vals) >= 4:
            labor_sales['month'] = parse_money(labor_vals[0])
            labor_sales['ytd'] = parse_money(labor_vals[1])
            labor_sales['py_month'] = parse_money(labor_vals[2])
            labor_sales['py_ytd'] = parse_money(labor_vals[3])
        
        # Q1 bonus targets
        new_equipment_target = 795000.00
        parts_target = 328000.00
        labor_target = 250000.00
        
        return {
            'new_equipment': new_equipment,
            'parts': parts_sales,
            'labor': labor_sales,
            'targets': {
                'new_equipment': new_equipment_target,
                'parts': parts_target,
                'labor': labor_target
            }
        }
    except Exception as e:
        print(f"Error parsing quarterly sales: {e}")
        return {
            'new_equipment': {'month': 0.0, 'ytd': 0.0},
            'parts': {'month': 0.0, 'ytd': 0.0},
            'labor': {'month': 0.0, 'ytd': 0.0},
            'targets': {'new_equipment': 795000.00, 'parts': 328000.00, 'labor': 250000.00}
        }

def parse_strategic_plan(filepath):
    """
    Parse Strategic Plan file with Quarterly Rocks,

 Annual Goals, and Issues List
    Format:
    === QUARTERLY ROCKS (Q1 2026 - Due: 3/31/2026) ===
    Rock description|Owner|Status
    
    === 2026 ANNUAL GOALS ===
    MetricName|Target|Current
    
    === ISSUES LIST ===
    IssueName|Priority
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        rocks = []
        goals = []
        issues = []
        quarter_info = ''
        
        sections = content.split('===')
        
        # Iterate through sections, pair headers with their data
        for i in range(len(sections)):
            section = sections[i].strip()
            if not section:
                continue
            
            # Check if this is a header section
            if 'QUARTERLY ROCKS' in section:
                quarter_info = section
                # Data is in the next section
                if i + 1 < len(sections):
                    data_section = sections[i + 1]
                    lines = data_section.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 3:
                                rocks.append({
                                    'description': parts[0].strip(),
                                    'owner': parts[1].strip(),
                                    'status': parts[2].strip()
                                })
            
            # Annual Goals Section
            elif 'ANNUAL GOALS' in section:
                # Data is in the next section
                if i + 1 < len(sections):
                    data_section = sections[i + 1]
                    lines = data_section.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 3:
                                try:
                                    target = float(parts[1].strip())
                                    current = float(parts[2].strip())
                                    percent = (current / target * 100) if target > 0 else 0
                                    goals.append({
                                        'name': parts[0].strip(),
                                        'target': target,
                                        'current': current,
                                        'percent': round(percent, 1)
                                    })
                                except:
                                    pass
            
            # Issues List Section
            elif 'ISSUES LIST' in section:
                # Data is in the next section
                if i + 1 < len(sections):
                    data_section = sections[i + 1]
                    lines = data_section.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 2:
                                issues.append({
                                    'description': parts[0].strip(),
                                    'priority': parts[1].strip()
                                })
        
        return {
            'quarter_info': quarter_info,
            'rocks': rocks,
            'goals': goals,
            'issues': issues
        }
    
    except Exception as e:
        print(f"Error parsing strategic plan: {e}")
        return {
            'quarter_info': '',
            'rocks': [],
            'goals': [],
            'issues': []
        }


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/data')
def get_data():
    """API endpoint to fetch all dashboard data"""
    
    # Get latest files
    schedule_file = get_latest_file('Scheduled Shop Jobs')
    backorders_file = get_latest_file('Open Back Orders')
    grossprofit_file = get_latest_file('Sales and Gross')
    quarterly_sales_file = get_latest_file('Site Lead')
    no_bins_file = get_latest_file(['No Bins', 'No Bin'])
    po_over_30_file = get_latest_file('PO Over 30')
    strategic_plan_file = get_latest_file('Strategic Plan')
    
    data = {
        'timestamp': datetime.now().isoformat(),
        'schedule': {'today': [], 'tomorrow': [], 'fit_ins': []},
        'parts_received': [],
        'mechanic_metrics': {'mechanics': [], 'overall_efficiency': 0},
        'quarterly_sales': {
            'new_equipment': {'month': 0.0, 'ytd': 0.0},
            'parts': {'month': 0.0, 'ytd': 0.0},
            'labor': {'month': 0.0, 'ytd': 0.0},
            'targets': {'new_equipment': 795000.00, 'parts': 328000.00, 'labor': 250000.00}
        },
        'no_bins': [],
        'backorders_over_5': [],
        'po_over_30': [],
        'strategic_plan': {
            'quarter_info': '',
            'rocks': [],
            'goals': [],
            'issues': []
        }
    }
    
    # Parse Shop Schedule
    if schedule_file:
        try:
            data['schedule'] = parse_shop_schedule(schedule_file)
        except Exception as e:
            data['schedule']['error'] = f"Could not read Shop Schedule file. Please resave it. Error: {str(e)}"
    
    # Parse Open Back Orders
    if backorders_file:
        data['parts_received'] = parse_open_back_orders(backorders_file)
        data['backorders_over_5'] = parse_backorders_over_5(backorders_file)
    
    # Parse Gross Profit Mechanic
    if grossprofit_file:
        data['mechanic_metrics'] = parse_gross_profit_mechanic(grossprofit_file)
    
    # Parse Quarterly Sales
    if quarterly_sales_file:
        data['quarterly_sales'] = parse_quarterly_sales(quarterly_sales_file)
    
    # Parse No Bins
    if no_bins_file:
        data['no_bins'] = parse_no_bins(no_bins_file)
    
    # Parse PO Over 30
    if po_over_30_file:
        data['po_over_30'] = parse_po_over_30(po_over_30_file)
    
    # Parse Strategic Plan
    if strategic_plan_file:
        data['strategic_plan'] = parse_strategic_plan(strategic_plan_file)
    
    return jsonify(data)

@app.route('/api/weather')
def get_weather():
    """Fetch current weather for Plainwell, MI"""
    try:
        import requests
        # Using wttr.in for simple weather data (no API key needed)
        response = requests.get('https://wttr.in/Plainwell,MI?format=j1', timeout=5)
        if response.status_code == 200:
            weather_data = response.json()
            current = weather_data['current_condition'][0]
            return jsonify({
                'temp': current['temp_F'],
                'condition': current['weatherDesc'][0]['value'],
                'icon': current['weatherCode']
            })
    except:
        pass
    
    return jsonify({'temp': '--', 'condition': 'Unknown', 'icon': '113'})

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Verify we can access data directory
        files_exist = os.path.exists(DATASHEETS_DIR)
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'datasheets_accessible': files_exist
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503

if __name__ == '__main__':
    # Create archive directory if it doesn't exist
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=5001, debug=False)
