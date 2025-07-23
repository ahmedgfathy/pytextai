#!/usr/bin/env python3
"""
Excel to CSV Merger Script
Safely merge Excel files with the main CSV without corrupting data
"""

import csv
import os
import sys
from pathlib import Path

def safe_excel_to_csv_merger():
    """
    Safely merge Excel files with main CSV
    Since we don't have pandas, we'll create a simple approach
    """
    
    print("🔍 Excel to CSV Merger - Safe Mode")
    print("=" * 50)
    
    # Check if main CSV exists
    main_csv = "whatsapp_chats.csv"
    if not os.path.exists(main_csv):
        print(f"❌ Error: {main_csv} not found!")
        return False
    
    # Check csvs folder
    csvs_folder = "csvs"
    if not os.path.exists(csvs_folder):
        print(f"❌ Error: {csvs_folder} folder not found!")
        return False
    
    # List Excel files
    excel_files = list(Path(csvs_folder).glob("*.xlsx"))
    if not excel_files:
        print("❌ No Excel files found in csvs folder!")
        return False
    
    print(f"📁 Found {len(excel_files)} Excel files:")
    for f in excel_files:
        print(f"   - {f.name}")
    
    print("\n⚠️  WARNING: This operation requires pandas and openpyxl!")
    print("❌ Cannot safely process Excel files without proper libraries.")
    print("\n📋 RECOMMENDATIONS:")
    print("1. Install required packages in a virtual environment")
    print("2. Convert Excel files to CSV manually first")
    print("3. Or use a system with pandas pre-installed")
    
    print("\n🔒 STOPPING to prevent data corruption")
    return False

def check_main_csv_structure():
    """Check the structure of the main CSV file"""
    try:
        with open("whatsapp_chats.csv", 'r', encoding='utf-8') as f:
            # Read first line to get headers
            first_line = f.readline().strip()
            headers = first_line.split(',')
            
            # Count total lines
            f.seek(0)
            total_lines = sum(1 for _ in f) - 1  # Subtract header
            
            print(f"📊 Main CSV Structure:")
            print(f"   Headers: {len(headers)} columns")
            print(f"   Data rows: {total_lines:,}")
            print(f"   Header columns: {', '.join(headers[:5])}...")
            
            return headers, total_lines
    except Exception as e:
        print(f"❌ Error reading main CSV: {e}")
        return None, 0

if __name__ == "__main__":
    print("🚀 Starting safe Excel processing check...")
    
    # Check main CSV first
    headers, total_rows = check_main_csv_structure()
    
    if headers:
        print(f"\n✅ Main CSV is valid with {total_rows:,} rows")
        
        # Try to merge Excel files
        success = safe_excel_to_csv_merger()
        
        if not success:
            print("\n💡 ALTERNATIVE SOLUTION:")
            print("1. Open each Excel file in LibreOffice Calc or Excel")
            print("2. Save each as CSV format")
            print("3. Then run this script to merge CSV files")
    else:
        print("❌ Cannot proceed - main CSV has issues")
