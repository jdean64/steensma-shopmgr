#!/usr/bin/env python3
"""
Excel File Repair Utility
Fixes corrupted Excel files by extracting data and creating clean copies
"""
import sys
import os
from zipfile import ZipFile
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

def fix_xlsx_file(input_file, output_file=None):
    """
    Attempt to fix a corrupted .xlsx file
    """
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_fixed{ext}"
    
    print(f"Attempting to repair: {input_file}")
    
    try:
        # Method 1: Try reading with xlrd (for older formats)
        print("  Method 1: Trying xlrd...")
        try:
            df = pd.read_excel(input_file, engine='xlrd')
            df.to_excel(output_file, index=False, engine='openpyxl')
            print(f"  ✓ Success! Saved to: {output_file}")
            return True
        except:
            print("    Failed with xlrd")
        
        # Method 2: Try extracting raw XML data
        print("  Method 2: Trying raw XML extraction...")
        try:
            import zipfile
            from lxml import etree
            
            # Extract workbook.xml
            with zipfile.ZipFile(input_file, 'r') as zip_ref:
                # Try to read the workbook
                with zip_ref.open('xl/workbook.xml') as f:
                    workbook_xml = f.read()
                
                # Try to read worksheets
                with zip_ref.open('xl/worksheets/sheet1.xml') as f:
                    sheet_xml = f.read()
            
            print("    Successfully extracted XML data")
            print("    Manual inspection required - check xl/workbook.xml and xl/worksheets/*.xml")
            
        except Exception as e:
            print(f"    Failed: {e}")
        
        # Method 3: Try pandas with different engines
        print("  Method 3: Trying different pandas engines...")
        for engine in ['openpyxl', 'xlrd', None]:
            try:
                print(f"    Trying engine: {engine}")
                if engine:
                    df = pd.read_excel(input_file, engine=engine)
                else:
                    df = pd.read_excel(input_file)
                
                # Save as CSV first (safer)
                csv_file = output_file.replace('.xlsx', '.csv').replace('.xls', '.csv')
                df.to_csv(csv_file, index=False)
                print(f"    ✓ Saved as CSV: {csv_file}")
                
                # Then save as Excel
                df.to_excel(output_file, index=False, engine='openpyxl')
                print(f"    ✓ Saved as Excel: {output_file}")
                return True
                
            except Exception as e:
                print(f"      Failed with {engine}: {str(e)[:100]}")
        
        print("\n  ✗ All automated repair methods failed.")
        print("\n  Manual steps required:")
        print("    1. Open the file in Microsoft Excel or LibreOffice")
        print("    2. Select all data (Ctrl+A)")
        print("    3. Copy (Ctrl+C)")
        print("    4. Create new workbook")
        print("    5. Paste (Ctrl+V)")
        print(f"    6. Save as: {output_file}")
        
        return False
        
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python fix_excel.py <input_file> [output_file]")
        print("\nExample:")
        print("  python fix_excel.py 'Shop Schedule - 5 Day - 1-15-26.xlsx'")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    success = fix_xlsx_file(input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
