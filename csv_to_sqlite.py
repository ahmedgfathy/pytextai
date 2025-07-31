#!/usr/bin/env python3
"""
CSV to SQLite Converter for Real Estate WhatsApp Data
Converts the merged CSV data into a SQLite database with proper schema.

Author: Real Estate Data Processing System
Date: 2025
"""

import sqlite3
import pandas as pd
import sys
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('csv_to_sqlite.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def create_database_schema(cursor):
    """Create the SQLite database schema for real estate data."""
    
    # Drop table if exists (for clean conversion)
    cursor.execute("DROP TABLE IF EXISTS properties")
    
    # Create the main properties table
    schema_sql = """
    CREATE TABLE properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        unique_id TEXT UNIQUE,
        file_source TEXT,
        date TEXT,
        time TEXT,
        sender_name TEXT,
        sender_phone TEXT,
        sender_phone_2 TEXT,
        message TEXT,
        message_backup TEXT,
        status TEXT,
        region TEXT,
        property_type TEXT,
        line_number INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- Indexes for better performance
        UNIQUE(unique_id)
    )
    """
    
    cursor.execute(schema_sql)
    
    # Create indexes for better query performance
    indexes = [
        "CREATE INDEX idx_date ON properties(date)",
        "CREATE INDEX idx_time ON properties(time)",
        "CREATE INDEX idx_sender_name ON properties(sender_name)",
        "CREATE INDEX idx_sender_phone ON properties(sender_phone)",
        "CREATE INDEX idx_region ON properties(region)",
        "CREATE INDEX idx_property_type ON properties(property_type)",
        "CREATE INDEX idx_file_source ON properties(file_source)",
        "CREATE INDEX idx_unique_id ON properties(unique_id)"
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    logging.info("Database schema created successfully")

def clean_data(df):
    """Clean and prepare the DataFrame for database insertion."""
    
    logging.info(f"Starting data cleaning. Shape: {df.shape}")
    
    # Handle missing values
    df = df.fillna('')
    
    # Clean text fields - remove excessive whitespace
    text_columns = ['sender_name', 'message', 'message_backup', 'region', 'property_type']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    
    # Ensure unique_id is string and not empty
    if 'unique_id' in df.columns:
        df['unique_id'] = df['unique_id'].astype(str)
        # Generate unique_id for empty ones
        empty_mask = (df['unique_id'] == '') | (df['unique_id'] == 'nan')
        if empty_mask.any():
            logging.warning(f"Found {empty_mask.sum()} empty unique_ids, generating new ones")
            df.loc[empty_mask, 'unique_id'] = [f"generated_{i}" for i in range(empty_mask.sum())]
    
    # Clean phone numbers
    phone_columns = ['sender_phone', 'sender_phone_2']
    for col in phone_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r'[^\d+]', '', regex=True)
    
    # Convert line_number to integer
    if 'line_number' in df.columns:
        df['line_number'] = pd.to_numeric(df['line_number'], errors='coerce').fillna(0).astype(int)
    
    logging.info(f"Data cleaning completed. Final shape: {df.shape}")
    return df

def import_csv_to_sqlite(csv_file, db_file, chunk_size=10000):
    """Import CSV data to SQLite database in chunks for memory efficiency."""
    
    if not os.path.exists(csv_file):
        logging.error(f"CSV file not found: {csv_file}")
        return False
    
    try:
        # Create database connection
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Create schema
        create_database_schema(cursor)
        
        # Get total rows for progress tracking
        total_rows = sum(1 for line in open(csv_file, 'r', encoding='utf-8')) - 1  # subtract header
        logging.info(f"Total rows to process: {total_rows:,}")
        
        processed_rows = 0
        chunk_num = 0
        
        # Process CSV in chunks
        for chunk in pd.read_csv(csv_file, chunksize=chunk_size, encoding='utf-8'):
            chunk_num += 1
            logging.info(f"Processing chunk {chunk_num} ({len(chunk)} rows)")
            
            # Clean the chunk
            chunk_cleaned = clean_data(chunk)
            
            # Insert into database
            try:
                chunk_cleaned.to_sql('properties', conn, if_exists='append', index=False, method='multi')
                processed_rows += len(chunk_cleaned)
                
                progress = (processed_rows / total_rows) * 100
                logging.info(f"Progress: {processed_rows:,}/{total_rows:,} ({progress:.1f}%)")
                
            except Exception as e:
                logging.error(f"Error inserting chunk {chunk_num}: {e}")
                # Try to insert row by row to identify problematic records
                for idx, row in chunk_cleaned.iterrows():
                    try:
                        row_df = pd.DataFrame([row])
                        row_df.to_sql('properties', conn, if_exists='append', index=False)
                        processed_rows += 1
                    except Exception as row_error:
                        logging.error(f"Error inserting row {idx}: {row_error}")
                        logging.error(f"Problematic row data: {row.to_dict()}")
        
        # Commit all changes
        conn.commit()
        
        # Verify the import
        cursor.execute("SELECT COUNT(*) FROM properties")
        db_count = cursor.fetchone()[0]
        
        logging.info(f"Import completed successfully!")
        logging.info(f"Records in database: {db_count:,}")
        logging.info(f"Records processed: {processed_rows:,}")
        
        # Get some statistics
        cursor.execute("SELECT COUNT(DISTINCT sender_name) FROM properties WHERE sender_name != ''")
        unique_senders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT region) FROM properties WHERE region != ''")
        unique_regions = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT property_type) FROM properties WHERE property_type != ''")
        unique_property_types = cursor.fetchone()[0]
        
        logging.info(f"Statistics:")
        logging.info(f"  - Unique senders: {unique_senders:,}")
        logging.info(f"  - Unique regions: {unique_regions:,}")
        logging.info(f"  - Unique property types: {unique_property_types:,}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        logging.error(f"Error during conversion: {e}")
        return False

def create_sample_queries_file():
    """Create a file with sample SQL queries for the database."""
    
    queries = """
-- Sample SQL Queries for Real Estate Database
-- File: sample_queries.sql

-- 1. Get total number of properties
SELECT COUNT(*) as total_properties FROM properties;

-- 2. Get properties by region
SELECT region, COUNT(*) as count 
FROM properties 
WHERE region != '' 
GROUP BY region 
ORDER BY count DESC;

-- 3. Get properties by type
SELECT property_type, COUNT(*) as count 
FROM properties 
WHERE property_type != '' 
GROUP BY property_type 
ORDER BY count DESC;

-- 4. Get most active senders
SELECT sender_name, COUNT(*) as messages_count
FROM properties 
WHERE sender_name != ''
GROUP BY sender_name 
ORDER BY messages_count DESC 
LIMIT 20;

-- 5. Search for properties containing specific keywords
SELECT unique_id, sender_name, region, property_type, message
FROM properties 
WHERE message LIKE '%شقة%' OR message LIKE '%apartment%'
LIMIT 50;

-- 6. Get properties by date range
SELECT date, COUNT(*) as count
FROM properties 
WHERE date != ''
GROUP BY date 
ORDER BY date DESC;

-- 7. Find properties with phone numbers
SELECT sender_name, sender_phone, message
FROM properties 
WHERE sender_phone != '' AND sender_phone != 'nan'
LIMIT 20;

-- 8. Get file source statistics
SELECT file_source, COUNT(*) as count
FROM properties 
GROUP BY file_source 
ORDER BY count DESC;

-- 9. Advanced search with multiple criteria
SELECT *
FROM properties 
WHERE region LIKE '%القاهرة%' 
  AND property_type != ''
  AND message LIKE '%للبيع%'
LIMIT 30;

-- 10. Get recent entries (if date format is consistent)
SELECT *
FROM properties 
WHERE created_at >= datetime('now', '-30 days')
ORDER BY created_at DESC;
"""
    
    with open('sample_queries.sql', 'w', encoding='utf-8') as f:
        f.write(queries)
    
    logging.info("Sample queries file created: sample_queries.sql")

def main():
    """Main function to run the CSV to SQLite conversion."""
    
    csv_file = 'whatsapp_chats.csv'
    db_file = 'real_estate_data.db'
    
    logging.info("Starting CSV to SQLite conversion")
    logging.info(f"Input CSV: {csv_file}")
    logging.info(f"Output DB: {db_file}")
    
    # Create backup if database already exists
    if os.path.exists(db_file):
        backup_name = f"real_estate_data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        os.rename(db_file, backup_name)
        logging.info(f"Existing database backed up as: {backup_name}")
    
    # Perform the conversion
    success = import_csv_to_sqlite(csv_file, db_file)
    
    if success:
        logging.info("✅ Conversion completed successfully!")
        logging.info(f"SQLite database created: {db_file}")
        
        # Create sample queries file
        create_sample_queries_file()
        
        # Display file sizes
        csv_size = os.path.getsize(csv_file) / (1024 * 1024)  # MB
        db_size = os.path.getsize(db_file) / (1024 * 1024)   # MB
        
        logging.info(f"File sizes:")
        logging.info(f"  - CSV: {csv_size:.1f} MB")
        logging.info(f"  - SQLite DB: {db_size:.1f} MB")
        logging.info(f"  - Compression ratio: {(csv_size/db_size):.1f}x")
        
    else:
        logging.error("❌ Conversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
