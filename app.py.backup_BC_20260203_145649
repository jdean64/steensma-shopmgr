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

def get_latest_file(pattern):
    """Get the most recent file matching a pattern"""
    files = [f for f in os.listdir(DATASHEETS_DIR) if pattern.lower() in f.lower()]
    if not files:
        return None
    latest = max(files, key=lambda f: os.path.getmtime(os.path.join(DATASHEETS_DIR, f)))
    return os.path.join(DATASHEETS_DIR, latest)

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
            today = datetime.now()
            tomorrow = today + timedelta(days=1)
            today_str = today.strftime('%-m/%-d/%Y')  # e.g., 1/15/2026
            tomorrow_str = tomorrow.strftime('%-m/%-d/%Y')
            
            lines = content.split('\n')
            current_mechanic = None
            in_fit_in_section = False
            
            for line in lines:
                line = line.strip()
                
                # Check for mechanic name
                if line.startswith('bDennis Smurr'):
                    current_mechanic = 'Dennis Smurr'
                    in_fit_in_section = False
                elif line.startswith('bJake Glas'):
                    current_mechanic = 'Jake Glas'
                    in_fit_in_section = False
                elif line.startswith('bRaymond Page'):
                    current_mechanic = 'Raymond Page'
                    in_fit_in_section = False
                elif line == 'FIT IN WORK':
                    in_fit_in_section = True
                    current_mechanic = 'Fit-In'
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
                        
                        # Add to fit-ins if in that section
                        if in_fit_in_section:
                            schedule_data['fit_ins'].append(job_data)
                        # Otherwise check date
                        elif start_time == today_str:
                            schedule_data['today'].append(job_data)
                        elif start_time == tomorrow_str:
                            schedule_data['tomorrow'].append(job_data)
            
            return schedule_data
        
        else:
            # Excel format
            # Try with openpyxl first, fallback to xlrd for .xls files
            if filepath.endswith('.xlsx'):
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
                df['ScheduledStartTime'] = pd.to_datetime(df['ScheduledStartTime'], errors='coerce')
                
                # Today's schedule
                today_df = df[df['ScheduledStartTime'].dt.date == today]
                for _, row in today_df.iterrows():
                    schedule_data['today'].append({
                        'customer': row.get('Customer', ''),
                        'job': row.get('Description', ''),
                        'mechanic': row.get('Mechanic', ''),
                        'time': row.get('ScheduledStartTime', '')
                    })
                
                # Tomorrow's schedule
                tomorrow_df = df[df['ScheduledStartTime'].dt.date == tomorrow.date()]
                for _, row in tomorrow_df.iterrows():
                    schedule_data['tomorrow'].append({
                        'customer': row.get('Customer', ''),
                        'job': row.get('Description', ''),
                        'mechanic': row.get('Mechanic', ''),
                        'time': row.get('ScheduledStartTime', '')
                    })
            
            # Find Fit-Ins (Mechanic column contains "Fit-In")
            if 'Mechanic' in df.columns:
                fit_in_df = df[df['Mechanic'].astype(str).str.contains('Fit-In', case=False, na=False)]
                for _, row in fit_in_df.iterrows():
                    schedule_data['fit_ins'].append({
                        'customer': row.get('Customer', ''),
                        'job': row.get('Description', ''),
                        'notes': row.get('Notes', '')
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
    Extract parts where Status is 'Received' or 'Released for Payment'
    """
    try:
        # Use xlrd for .xls files
        df = pd.read_excel(filepath, engine='xlrd')
        
        parts_received = []
        
        # The header is at row 4 (index 4)
        # Customer is column 1, Part Number is column 9, Status is column 17
        # Re-read with proper header
        df = pd.read_excel(filepath, engine='xlrd', header=4)
        
        # Clean up column names
        df.columns = [str(col).strip() if pd.notna(col) else f'Col_{i}' for i, col in enumerate(df.columns)]
        
        # Find columns by name or position
        customer_col = 'Customer' if 'Customer' in df.columns else df.columns[1]
        part_col = df.columns[9]  # Part number is at column index 9
        status_col = 'Status' if 'Status' in df.columns else df.columns[17]
        
        # Filter for Received or Released for Payment
        for _, row in df.iterrows():
            status = str(row[status_col]).strip() if pd.notna(row[status_col]) else ''
            part_number = str(row[part_col]).strip() if pd.notna(row[part_col]) else ''
            customer = str(row[customer_col]).strip() if pd.notna(row[customer_col]) else ''
            
            # Check if status contains Received or Released
            if ('received' in status.lower() or 'released' in status.lower()) and part_number and part_number != 'nan':
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
                # Match mechanic summary lines - they start with 'b' and mechanic name
                if line.startswith('bDennis Smurr,') and len(line) > 50:
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
                            'name': 'Dennis Smurr',
                            'efficiency': 0,  # Will update from Hours Worked line
                            'labor_sales': labor_sales
                        })
                
                elif line.startswith('bJake Glas,') and len(line) > 50:
                    dollar_amounts = re.findall(r'\$[\d,]+\.?\d*', line)
                    if len(dollar_amounts) >= 3:
                        labor_sales = dollar_amounts[2].replace('$', '').replace(',', '')
                        try:
                            labor_sales = float(labor_sales)
                        except:
                            labor_sales = 0
                        
                        mechanic_metrics.append({
                            'name': 'Jake Glas',
                            'efficiency': 0,
                            'labor_sales': labor_sales
                        })
                
                elif line.startswith('bRaymond Page,') and len(line) > 50:
                    dollar_amounts = re.findall(r'\$[\d,]+\.?\d*', line)
                    if len(dollar_amounts) >= 3:
                        labor_sales = dollar_amounts[2].replace('$', '').replace(',', '')
                        try:
                            labor_sales = float(labor_sales)
                        except:
                            labor_sales = 0
                        
                        mechanic_metrics.append({
                            'name': 'Ray Page',
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
        
        # If not a text file, try Excel parsing
        else:
            df = pd.read_excel(filepath, engine='xlrd')
            
            mechanics = {
                'Dennis Smurr': {'efficiency_cell': 'G120', 'labor_cell': 'O119'},
                'Jake Glas': {'efficiency_cell': 'G189', 'labor_cell': 'O188'},
                'Ray Page': {'efficiency_cell': 'G233', 'labor_cell': 'O232'}
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
    
    data = {
        'timestamp': datetime.now().isoformat(),
        'schedule': {'today': [], 'tomorrow': [], 'fit_ins': []},
        'parts_received': [],
        'mechanic_metrics': {'mechanics': [], 'overall_efficiency': 0}
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
    
    # Parse Gross Profit Mechanic
    if grossprofit_file:
        data['mechanic_metrics'] = parse_gross_profit_mechanic(grossprofit_file)
    
    return jsonify(data)

@app.route('/api/weather')
def get_weather():
    """Fetch current weather for Battle Creek, MI"""
    try:
        import requests
        # Using wttr.in for simple weather data (no API key needed)
        response = requests.get('https://wttr.in/Battle+Creek,MI?format=j1', timeout=5)
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

if __name__ == '__main__':
    # Create archive directory if it doesn't exist
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    # Run the app
    app.run(host='0.0.0.0', port=5001, debug=True)
