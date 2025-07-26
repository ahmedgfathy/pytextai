#!/usr/bin/env python3
"""
Safe Excel to CSV Merger
Merges Excel files from csvs/ folder with the main CSV safely
"""

import pandas as pd
import os
import sys
from datetime import datetime

def backup_main_csv():
    """Create a timestamped backup of the main CSV"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"whatsapp_chats_backup_{timestamp}.csv"
    
    if os.path.exists("whatsapp_chats.csv"):
        os.system(f"cp whatsapp_chats.csv {backup_name}")
        print(f"✅ Backup created: {backup_name}")
        return backup_name
    return None

def read_main_csv():
    """Read the main CSV file"""
    try:
        df = pd.read_csv("whatsapp_chats.csv", encoding='utf-8')
        print(f"📊 Main CSV loaded: {len(df)} rows, {len(df.columns)} columns")
        return df
    except Exception as e:
        print(f"❌ Error reading main CSV: {e}")
        return None

def process_excel_files():
    """Process all Excel files in csvs/ folder"""
    csvs_dir = "csvs"
    if not os.path.exists(csvs_dir):
        print(f"❌ {csvs_dir} folder not found!")
        return []
    
    excel_files = [f for f in os.listdir(csvs_dir) if f.endswith('.xlsx')]
    if not excel_files:
        print("❌ No Excel files found!")
        return []
    
    print(f"📁 Found {len(excel_files)} Excel files:")
    
    all_dataframes = []
    
    for excel_file in excel_files:
        excel_path = os.path.join(csvs_dir, excel_file)
        print(f"\n🔍 Processing: {excel_file}")
        
        try:
            # Read all sheets from Excel file
            excel_data = pd.read_excel(excel_path, sheet_name=None, engine='openpyxl')
            
            for sheet_name, df in excel_data.items():
                if df.empty:
                    print(f"   ⚠️  Sheet '{sheet_name}' is empty, skipping")
                    continue
                
                print(f"   📄 Sheet '{sheet_name}': {len(df)} rows, {len(df.columns)} columns")
                print(f"      Columns: {list(df.columns)}")
                
                # Add metadata columns
                df['excel_source'] = excel_file
                df['sheet_name'] = sheet_name
                df['import_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                all_dataframes.append(df)
                
        except Exception as e:
            print(f"   ❌ Error processing {excel_file}: {e}")
            continue
    
    return all_dataframes

def safe_merge_data(main_df, excel_dataframes):
    """Safely merge Excel data with main CSV"""
    if not excel_dataframes:
        print("❌ No Excel data to merge")
        return main_df
    
    print(f"\n🔄 Merging {len(excel_dataframes)} Excel sheets with main CSV...")
    
    # Get main CSV column count
    main_columns = len(main_df.columns)
    next_unique_id = len(main_df) + 1
    
    # Process each Excel dataframe
    merged_rows = []
    
    for i, excel_df in enumerate(excel_dataframes):
        print(f"   Processing sheet {i+1}/{len(excel_dataframes)}...")
        
        # Create new rows based on Excel data
        for idx, row in excel_df.iterrows():
            # Create a new row with main CSV structure
            new_row = {}
            
            # Generate unique ID
            new_row['unique_id'] = f"EXL{next_unique_id}"
            next_unique_id += 1
            
            # Map Excel columns to main CSV columns (customize as needed)
            new_row['file_source'] = f"excel/{row.get('excel_source', 'unknown.xlsx')}"
            new_row['date'] = datetime.now().strftime("%d/%m/%Y")
            new_row['time'] = datetime.now().strftime("%I:%M:%S %p")
            
            # Try to map common fields
            possible_name_fields = ['name', 'sender', 'client_name', 'اسم العميل', 'الاسم']
            possible_phone_fields = ['phone', 'mobile', 'telephone', 'رقم الهاتف', 'الهاتف']
            possible_message_fields = ['message', 'description', 'details', 'الرسالة', 'التفاصيل']
            possible_property_fields = ['property_type', 'type', 'نوع العقار']
            possible_status_fields = ['status', 'حالة', 'الحالة']
            possible_region_fields = ['region', 'area', 'location', 'المنطقة', 'الموقع']
            
            # Map fields
            new_row['sender_name'] = find_field_value(row, possible_name_fields) or 'من Excel'
            new_row['sender_phone'] = find_field_value(row, possible_phone_fields) or ''
            new_row['sender_phone_2'] = ''
            new_row['message'] = find_field_value(row, possible_message_fields) or str(row.to_dict())
            new_row['message_backup'] = new_row['message']
            new_row['status'] = find_field_value(row, possible_status_fields) or ''
            new_row['region'] = find_field_value(row, possible_region_fields) or ''
            new_row['property_type'] = find_field_value(row, possible_property_fields) or ''
            new_row['line_number'] = idx + 1
            
            merged_rows.append(new_row)
    
    # Convert to DataFrame
    if merged_rows:
        excel_df_combined = pd.DataFrame(merged_rows)
        
        # Combine with main data
        result_df = pd.concat([main_df, excel_df_combined], ignore_index=True)
        
        print(f"✅ Merge completed!")
        print(f"   Original rows: {len(main_df)}")
        print(f"   New rows from Excel: {len(merged_rows)}")
        print(f"   Total rows: {len(result_df)}")
        
        return result_df
    else:
        print("⚠️  No data was extracted from Excel files")
        return main_df

def find_field_value(row, possible_fields):
    """Find a field value from possible field names"""
    for field in possible_fields:
        if field in row and pd.notna(row[field]):
            return str(row[field])
    return None

def main():
    print("🚀 Safe Excel to CSV Merger")
    print("=" * 50)
    
    # Step 1: Backup main CSV
    backup_file = backup_main_csv()
    if not backup_file:
        print("❌ Could not create backup. Stopping for safety.")
        return False
    
    # Step 2: Read main CSV
    main_df = read_main_csv()
    if main_df is None:
        print("❌ Could not read main CSV. Stopping.")
        return False
    
    # Step 3: Process Excel files
    excel_dataframes = process_excel_files()
    if not excel_dataframes:
        print("❌ No Excel data to process.")
        return False
    
    # Step 4: Ask for confirmation
    print(f"\n⚠️  CONFIRMATION REQUIRED:")
    print(f"   📊 Main CSV: {len(main_df)} rows")
    print(f"   📁 Excel sheets: {len(excel_dataframes)} sheets to process")
    print(f"   💾 Backup created: {backup_file}")
    
    response = input(f"\nProceed with merge? (yes/no): ").lower()
    if response != 'yes':
        print("❌ Merge cancelled by user")
        return False
    
    # Step 5: Merge data
    result_df = safe_merge_data(main_df, excel_dataframes)
    
    # Step 6: Save result
    try:
        result_df.to_csv("whatsapp_chats.csv", index=False, encoding='utf-8')
        print(f"\n✅ SUCCESS!")
        print(f"   📄 Updated CSV saved: whatsapp_chats.csv")
        print(f"   📊 Total records: {len(result_df)}")
        print(f"   💾 Backup available: {backup_file}")
        
        # Show summary
        original_count = len(main_df)
        new_count = len(result_df) - original_count
        print(f"\n📈 SUMMARY:")
        print(f"   Original records: {original_count:,}")
        print(f"   New records added: {new_count:,}")
        print(f"   Total records: {len(result_df):,}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving merged data: {e}")
        print(f"🔄 Restoring backup...")
        if backup_file and os.path.exists(backup_file):
            os.system(f"cp {backup_file} whatsapp_chats.csv")
            print("✅ Backup restored")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print(f"\n🎉 Your HTML viewer will now show ALL data!")
        print(f"   Refresh your browser to see the updated data.")
    else:
        print(f"\n⚠️  Merge failed. Your original data is safe.")
    
    sys.exit(0 if success else 1)
