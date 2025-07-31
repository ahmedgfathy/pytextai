#!/usr/bin/env python3
"""
SQLite Database Query Utility for Real Estate Data
Provides easy methods to query and interact with the SQLite database.

Author: Real Estate Data Processing System
Date: 2025
"""

import sqlite3
import pandas as pd
import sys
from datetime import datetime

class RealEstateDB:
    """Class to interact with the real estate SQLite database."""
    
    def __init__(self, db_path='real_estate_data.db'):
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to the database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the database."""
        if self.conn:
            self.conn.close()
    
    def execute_query(self, query, params=None):
        """Execute a query and return results as DataFrame."""
        try:
            if params:
                df = pd.read_sql_query(query, self.conn, params=params)
            else:
                df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
    
    def get_stats(self):
        """Get basic database statistics."""
        stats = {}
        
        # Total properties
        result = self.execute_query("SELECT COUNT(*) as total FROM properties")
        stats['total_properties'] = result.iloc[0]['total'] if result is not None else 0
        
        # Unique senders
        result = self.execute_query("SELECT COUNT(DISTINCT sender_name) as count FROM properties WHERE sender_name != ''")
        stats['unique_senders'] = result.iloc[0]['count'] if result is not None else 0
        
        # Unique regions
        result = self.execute_query("SELECT COUNT(DISTINCT region) as count FROM properties WHERE region != ''")
        stats['unique_regions'] = result.iloc[0]['count'] if result is not None else 0
        
        # Unique property types
        result = self.execute_query("SELECT COUNT(DISTINCT property_type) as count FROM properties WHERE property_type != ''")
        stats['unique_property_types'] = result.iloc[0]['count'] if result is not None else 0
        
        return stats
    
    def search_properties(self, keyword, limit=50):
        """Search for properties containing a keyword."""
        query = """
        SELECT unique_id, sender_name, region, property_type, message, date, time
        FROM properties 
        WHERE message LIKE ? OR region LIKE ? OR property_type LIKE ?
        ORDER BY date DESC, time DESC
        LIMIT ?
        """
        keyword_pattern = f"%{keyword}%"
        return self.execute_query(query, (keyword_pattern, keyword_pattern, keyword_pattern, limit))
    
    def get_properties_by_region(self, region, limit=100):
        """Get properties from a specific region."""
        query = """
        SELECT unique_id, sender_name, property_type, message, date, time
        FROM properties 
        WHERE region LIKE ?
        ORDER BY date DESC, time DESC
        LIMIT ?
        """
        return self.execute_query(query, (f"%{region}%", limit))
    
    def get_properties_by_sender(self, sender_name, limit=100):
        """Get properties from a specific sender."""
        query = """
        SELECT unique_id, region, property_type, message, date, time
        FROM properties 
        WHERE sender_name LIKE ?
        ORDER BY date DESC, time DESC
        LIMIT ?
        """
        return self.execute_query(query, (f"%{sender_name}%", limit))
    
    def get_top_regions(self, limit=20):
        """Get regions with most properties."""
        query = """
        SELECT region, COUNT(*) as count
        FROM properties 
        WHERE region != ''
        GROUP BY region 
        ORDER BY count DESC
        LIMIT ?
        """
        return self.execute_query(query, (limit,))
    
    def get_top_senders(self, limit=20):
        """Get senders with most messages."""
        query = """
        SELECT sender_name, COUNT(*) as messages_count
        FROM properties 
        WHERE sender_name != ''
        GROUP BY sender_name 
        ORDER BY messages_count DESC
        LIMIT ?
        """
        return self.execute_query(query, (limit,))
    
    def get_property_types(self):
        """Get all property types and their counts."""
        query = """
        SELECT property_type, COUNT(*) as count
        FROM properties 
        WHERE property_type != ''
        GROUP BY property_type 
        ORDER BY count DESC
        """
        return self.execute_query(query)
    
    def export_to_csv(self, query, filename, params=None):
        """Export query results to CSV."""
        try:
            df = self.execute_query(query, params)
            if df is not None:
                df.to_csv(filename, index=False, encoding='utf-8')
                print(f"Results exported to: {filename}")
                return True
            return False
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

def main():
    """Main function demonstrating database usage."""
    
    # Initialize database
    db = RealEstateDB()
    
    if not db.connect():
        print("Failed to connect to database")
        sys.exit(1)
    
    print("🏠 Real Estate Database Query Utility")
    print("=" * 50)
    
    # Get and display basic stats
    print("\n📊 Database Statistics:")
    stats = db.get_stats()
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value:,}")
    
    # Interactive mode
    while True:
        print("\n" + "=" * 50)
        print("Available Commands:")
        print("1. Search properties (keyword)")
        print("2. Get top regions")
        print("3. Get top senders")
        print("4. Get property types")
        print("5. Properties by region")
        print("6. Properties by sender")
        print("7. Custom SQL query")
        print("8. Export data to CSV")
        print("9. Exit")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == '1':
            keyword = input("Enter search keyword: ").strip()
            if keyword:
                results = db.search_properties(keyword)
                if results is not None and not results.empty:
                    print(f"\nFound {len(results)} properties:")
                    print(results.to_string(max_rows=10))
                else:
                    print("No properties found.")
        
        elif choice == '2':
            results = db.get_top_regions()
            if results is not None and not results.empty:
                print("\nTop Regions:")
                print(results.to_string(index=False))
        
        elif choice == '3':
            results = db.get_top_senders()
            if results is not None and not results.empty:
                print("\nTop Senders:")
                print(results.to_string(index=False))
        
        elif choice == '4':
            results = db.get_property_types()
            if results is not None and not results.empty:
                print("\nProperty Types:")
                print(results.to_string(index=False))
        
        elif choice == '5':
            region = input("Enter region name: ").strip()
            if region:
                results = db.get_properties_by_region(region)
                if results is not None and not results.empty:
                    print(f"\nProperties in {region}:")
                    print(results.to_string(max_rows=10))
                else:
                    print("No properties found in this region.")
        
        elif choice == '6':
            sender = input("Enter sender name: ").strip()
            if sender:
                results = db.get_properties_by_sender(sender)
                if results is not None and not results.empty:
                    print(f"\nProperties from {sender}:")
                    print(results.to_string(max_rows=10))
                else:
                    print("No properties found from this sender.")
        
        elif choice == '7':
            query = input("Enter SQL query: ").strip()
            if query:
                results = db.execute_query(query)
                if results is not None and not results.empty:
                    print(f"\nQuery Results:")
                    print(results.to_string(max_rows=20))
                else:
                    print("No results or query error.")
        
        elif choice == '8':
            query = input("Enter SQL query for export: ").strip()
            filename = input("Enter output filename (with .csv): ").strip()
            if query and filename:
                db.export_to_csv(query, filename)
        
        elif choice == '9':
            break
        
        else:
            print("Invalid choice. Please try again.")
    
    db.disconnect()
    print("Goodbye!")

if __name__ == "__main__":
    main()
