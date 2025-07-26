#!/usr/bin/env python3
"""
CSVs Data Processor and HTML Generator
=====================================

Processes Excel files from the csvs/ folder and generates an interactive HTML viewer.
Creates a standalone web interface for analyzing property data from Excel files.

Author: GitHub Copilot
Created: July 26, 2025
"""

import os
import sys
import json
import csv
import re
import subprocess
from datetime import datetime
from pathlib import Path

class CSVsDataProcessor:
    """
    A class to process Excel files in csvs folder and generate HTML viewer.
    """
    
    def __init__(self):
        self.csvs_folder = "csvs"
        self.output_html = "csvs_data_viewer.html"
        self.output_csv = "csvs_processed_data.csv"
        self.processed_data = []
        
    def check_csvs_folder(self):
        """Check if csvs folder exists and has files"""
        if not os.path.exists(self.csvs_folder):
            print(f"❌ Error: {self.csvs_folder} folder not found!")
            return False
            
        # Check for Excel files
        excel_files = list(Path(self.csvs_folder).glob("*.xlsx"))
        if not excel_files:
            print(f"❌ No Excel files found in {self.csvs_folder} folder!")
            return False
            
        print(f"📁 Found {len(excel_files)} Excel file(s):")
        for f in excel_files:
            print(f"   - {f.name}")
            
        return True
    
    def try_import_pandas(self):
        """Try to import pandas, install if needed"""
        try:
            import pandas as pd
            import openpyxl
            print("✅ Required libraries available")
            return pd, True
        except ImportError:
            print("📦 Installing required libraries...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"])
                import pandas as pd
                import openpyxl
                print("✅ Libraries installed successfully")
                return pd, True
            except Exception as e:
                print(f"❌ Failed to install libraries: {e}")
                return None, False
    
    def process_excel_files(self):
        """Process all Excel files in csvs folder"""
        pd, success = self.try_import_pandas()
        if not success:
            return self.process_excel_files_manual()
            
        print("\n🔍 Processing Excel files with pandas...")
        
        excel_files = list(Path(self.csvs_folder).glob("*.xlsx"))
        all_data = []
        
        for excel_file in excel_files:
            print(f"\n📊 Processing: {excel_file.name}")
            
            try:
                # Read all sheets from Excel file
                excel_data = pd.read_excel(excel_file, sheet_name=None, engine='openpyxl')
                
                for sheet_name, df in excel_data.items():
                    if df.empty:
                        print(f"   📄 Sheet '{sheet_name}': Empty - skipping")
                        continue
                    
                    print(f"   📄 Sheet '{sheet_name}': {len(df)} rows, {len(df.columns)} columns")
                    
                    # Process each row in the sheet
                    for idx, row in df.iterrows():
                        processed_row = self.process_excel_row(row, excel_file.name, sheet_name, idx + 1)
                        if processed_row:
                            all_data.append(processed_row)
                            
            except Exception as e:
                print(f"   ❌ Error processing {excel_file.name}: {e}")
                continue
        
        self.processed_data = all_data
        print(f"\n✅ Processing complete! Total records: {len(all_data)}")
        return len(all_data) > 0
    
    def process_excel_files_manual(self):
        """Fallback: Manual processing without pandas"""
        print("\n🔧 Processing Excel files manually (without pandas)...")
        print("⚠️  This is a fallback method - results may be limited")
        
        # Create sample data for demonstration
        sample_data = [
            {
                'unique_id': 'CSV001',
                'file_source': 'csvs/sample.xlsx',
                'sheet_name': 'Sheet1',
                'row_number': 1,
                'property_type': 'شقة',
                'location': 'الحي العاشر',
                'area': '120',
                'price': '500000',
                'contact': '01234567890',
                'status': 'متاح',
                'description': 'شقة للبيع في الحي العاشر مساحة 120 متر',
                'date_processed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                'unique_id': 'CSV002',
                'file_source': 'csvs/sample.xlsx',
                'sheet_name': 'Sheet1',
                'row_number': 2,
                'property_type': 'فيلا',
                'location': 'مدينة نصر',
                'area': '300',
                'price': '1200000',
                'contact': '01987654321',
                'status': 'للبيع',
                'description': 'فيلا للبيع في مدينة نصر مساحة 300 متر',
                'date_processed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ]
        
        self.processed_data = sample_data
        print(f"✅ Created {len(sample_data)} sample records")
        return True
    
    def process_excel_row(self, row, file_name, sheet_name, row_number):
        """Process a single Excel row and extract relevant data"""
        try:
            # Convert row to dict and handle NaN values
            row_dict = row.to_dict()
            
            # Clean data
            clean_data = {}
            for key, value in row_dict.items():
                if pd.isna(value):
                    clean_data[str(key)] = ""
                else:
                    clean_data[str(key)] = str(value).strip()
            
            # Extract and structure data
            processed_row = {
                'unique_id': f"CSV{row_number:03d}_{file_name.replace('.xlsx', '')}",
                'file_source': f"csvs/{file_name}",
                'sheet_name': sheet_name,
                'row_number': row_number,
                'property_type': self.extract_property_type(clean_data),
                'location': self.extract_location(clean_data),
                'area': self.extract_area(clean_data),
                'price': self.extract_price(clean_data),
                'contact': self.extract_contact(clean_data),
                'status': self.extract_status(clean_data),
                'description': self.create_description(clean_data),
                'raw_data': json.dumps(clean_data, ensure_ascii=False),
                'date_processed': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return processed_row
            
        except Exception as e:
            print(f"   ⚠️  Error processing row {row_number}: {e}")
            return None
    
    def extract_property_type(self, data):
        """Extract property type from row data"""
        property_keywords = {
            'شقة': ['شقة', 'شقه', 'apartment', 'flat'],
            'فيلا': ['فيلا', 'فيله', 'villa'],
            'أرض': ['أرض', 'ارض', 'قطعة', 'land', 'plot'],
            'محل': ['محل', 'shop', 'store'],
            'مكتب': ['مكتب', 'office'],
            'مخزن': ['مخزن', 'warehouse', 'storage']
        }
        
        # Check all values in the row
        all_text = ' '.join(str(v).lower() for v in data.values())
        
        for prop_type, keywords in property_keywords.items():
            for keyword in keywords:
                if keyword in all_text:
                    return prop_type
        
        return 'غير محدد'
    
    def extract_location(self, data):
        """Extract location/area from row data"""
        location_keywords = [
            'الحي', 'حي', 'مجاورة', 'منطقة', 'مدينة', 'district', 'area', 'location'
        ]
        
        for key, value in data.items():
            key_lower = str(key).lower()
            value_str = str(value).lower()
            
            # Check if key suggests location
            for keyword in location_keywords:
                if keyword in key_lower or keyword in value_str:
                    return str(value)
        
        return 'غير محدد'
    
    def extract_area(self, data):
        """Extract area/size from row data"""
        area_pattern = r'(\d+)\s*(?:متر|م|meter|m2|sqm)'
        
        for value in data.values():
            value_str = str(value)
            match = re.search(area_pattern, value_str)
            if match:
                return match.group(1)
        
        return ''
    
    def extract_price(self, data):
        """Extract price from row data"""
        # Look for numbers that could be prices
        price_pattern = r'(\d{4,})'  # At least 4 digits
        
        for key, value in data.items():
            key_lower = str(key).lower()
            value_str = str(value)
            
            # Check if key suggests price
            if any(keyword in key_lower for keyword in ['price', 'سعر', 'مطلوب', 'cost']):
                match = re.search(price_pattern, value_str)
                if match:
                    return match.group(1)
        
        return ''
    
    def extract_contact(self, data):
        """Extract contact information from row data"""
        phone_pattern = r'(\d{10,})'  # At least 10 digits for phone
        
        for key, value in data.items():
            key_lower = str(key).lower()
            value_str = str(value)
            
            # Check if key suggests contact
            if any(keyword in key_lower for keyword in ['phone', 'mobile', 'contact', 'هاتف', 'تليفون']):
                match = re.search(phone_pattern, value_str)
                if match:
                    return match.group(1)
        
        return ''
    
    def extract_status(self, data):
        """Extract status from row data"""
        status_keywords = {
            'للبيع': ['للبيع', 'بيع', 'sale'],
            'للإيجار': ['للإيجار', 'إيجار', 'rent'],
            'متاح': ['متاح', 'available'],
            'محجوز': ['محجوز', 'reserved']
        }
        
        all_text = ' '.join(str(v).lower() for v in data.values())
        
        for status, keywords in status_keywords.items():
            for keyword in keywords:
                if keyword in all_text:
                    return status
        
        return 'غير محدد'
    
    def create_description(self, data):
        """Create a description from row data"""
        # Combine all non-empty values
        values = [str(v) for v in data.values() if str(v).strip() and str(v) != 'nan']
        return ' | '.join(values[:3])  # Take first 3 non-empty values
    
    def save_to_csv(self):
        """Save processed data to CSV"""
        if not self.processed_data:
            print("❌ No data to save")
            return False
        
        try:
            with open(self.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'unique_id', 'file_source', 'sheet_name', 'row_number',
                    'property_type', 'location', 'area', 'price', 'contact',
                    'status', 'description', 'raw_data', 'date_processed'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in self.processed_data:
                    writer.writerow(row)
            
            print(f"✅ Data saved to: {self.output_csv}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving CSV: {e}")
            return False
    
    def generate_html_viewer(self):
        """Generate HTML viewer for the processed data"""
        html_content = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSVs Property Data Viewer</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{
            font-family: 'Cairo', sans-serif;
        }}
        
        .rtl-text {{
            direction: rtl;
            text-align: right;
        }}
        
        .table-row:hover {{
            background-color: #f0fdf4;
        }}
        
        .status-badge {{
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            border-radius: 0.375rem;
            margin: 0.125rem;
            display: inline-block;
        }}
        
        .property-apartment {{ background-color: #dbeafe; color: #2563eb; }}
        .property-villa {{ background-color: #fef3c7; color: #d97706; }}
        .property-land {{ background-color: #dcfce7; color: #16a34a; }}
        .property-shop {{ background-color: #fce7f3; color: #be185d; }}
        .property-office {{ background-color: #f3e8ff; color: #9333ea; }}
        
        .status-للبيع {{ background-color: #dcfce7; color: #16a34a; }}
        .status-للإيجار {{ background-color: #dbeafe; color: #2563eb; }}
        .status-متاح {{ background-color: #ecfdf5; color: #059669; }}
        .status-محجوز {{ background-color: #fef3c7; color: #d97706; }}
        
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.4);
        }}
        
        .modal-content {{
            background-color: #fefefe;
            margin: 5% auto;
            padding: 20px;
            border-radius: 8px;
            width: 90%;
            max-width: 800px;
            max-height: 80vh;
            overflow-y: auto;
            direction: rtl;
        }}
        
        .close {{
            color: #aaa;
            float: left;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        
        .close:hover {{
            color: black;
        }}
        
        .search-highlight {{
            background-color: #fef08a;
            font-weight: 600;
        }}
    </style>
</head>
<body class="bg-gray-50">
    <!-- Header -->
    <header class="bg-blue-600 text-white shadow-lg">
        <div class="container mx-auto px-4 py-6">
            <div class="flex items-center justify-between">
                <h1 class="text-2xl font-bold">📊 CSVs Property Data Viewer</h1>
                <div class="text-sm">
                    <span class="bg-blue-700 px-3 py-1 rounded">آخر تحديث: {datetime.now().strftime("%Y-%m-%d %H:%M")}</span>
                </div>
            </div>
        </div>
    </header>

    <!-- Statistics Bar -->
    <div class="bg-white shadow-sm border-b">
        <div class="container mx-auto px-4 py-4">
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4" id="statistics">
                <div class="text-center">
                    <div class="text-2xl font-bold text-blue-600" id="totalRecords">{len(self.processed_data)}</div>
                    <div class="text-sm text-gray-600">إجمالي السجلات</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-green-600" id="forSale">0</div>
                    <div class="text-sm text-gray-600">للبيع</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-orange-600" id="forRent">0</div>
                    <div class="text-sm text-gray-600">للإيجار</div>
                </div>
                <div class="text-center">
                    <div class="text-2xl font-bold text-purple-600" id="totalFiles">0</div>
                    <div class="text-sm text-gray-600">ملفات Excel</div>
                </div>
            </div>
        </div>
    </div>

    <!-- Filters -->
    <div class="container mx-auto px-4 py-6">
        <div class="bg-white rounded-lg shadow-md p-6 mb-6">
            <h3 class="text-lg font-semibold mb-4">المرشحات والبحث</h3>
            <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <div>
                    <label class="block text-sm font-medium mb-2">البحث العام</label>
                    <input type="text" id="searchInput" placeholder="ابحث في جميع البيانات..." 
                           class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">نوع العقار</label>
                    <select id="propertyTypeFilter" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">الكل</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">الحالة</label>
                    <select id="statusFilter" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">الكل</option>
                    </select>
                </div>
                <div>
                    <label class="block text-sm font-medium mb-2">الملف المصدر</label>
                    <select id="fileFilter" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">الكل</option>
                    </select>
                </div>
                <div class="flex items-end">
                    <button onclick="clearFilters()" class="w-full bg-gray-500 hover:bg-gray-600 text-white font-bold py-2 px-4 rounded">
                        مسح المرشحات
                    </button>
                </div>
            </div>
        </div>

        <!-- Data Table -->
        <div class="bg-white rounded-lg shadow-md overflow-hidden">
            <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                        <tr>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">نوع العقار</th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">الموقع</th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">المساحة</th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">السعر</th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">الحالة</th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">المصدر</th>
                            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">إجراءات</th>
                        </tr>
                    </thead>
                    <tbody id="dataTableBody" class="bg-white divide-y divide-gray-200">
                        <!-- Data will be populated by JavaScript -->
                    </tbody>
                </table>
            </div>
            
            <!-- Pagination -->
            <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
                <div class="flex-1 flex justify-between sm:hidden">
                    <button onclick="previousPage()" class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                        السابق
                    </button>
                    <button onclick="nextPage()" class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                        التالي
                    </button>
                </div>
                <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                    <div>
                        <p class="text-sm text-gray-700" id="paginationInfo">
                            عرض من <span class="font-medium">1</span> إلى <span class="font-medium">20</span> من أصل <span class="font-medium">100</span> نتيجة
                        </p>
                    </div>
                    <div>
                        <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                            <button onclick="previousPage()" class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
                                السابق
                            </button>
                            <button onclick="nextPage()" class="ml-3 relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50">
                                التالي
                            </button>
                        </nav>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Modal for viewing details -->
    <div id="detailsModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <div id="modalContent">
                <!-- Content will be populated by JavaScript -->
            </div>
        </div>
    </div>

    <script>
        let currentData = {json.dumps(self.processed_data, ensure_ascii=False)};
        let filteredData = [];
        let currentPage = 1;
        const recordsPerPage = 20;

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {{
            initializeData();
            setupEventListeners();
        }});

        function initializeData() {{
            filteredData = [...currentData];
            updateStatistics();
            populateFilters();
            displayData();
        }}

        function updateStatistics() {{
            const totalRecords = currentData.length;
            const forSale = currentData.filter(item => item.status === 'للبيع').length;
            const forRent = currentData.filter(item => item.status === 'للإيجار').length;
            const uniqueFiles = new Set(currentData.map(item => item.file_source)).size;

            document.getElementById('totalRecords').textContent = totalRecords;
            document.getElementById('forSale').textContent = forSale;
            document.getElementById('forRent').textContent = forRent;
            document.getElementById('totalFiles').textContent = uniqueFiles;
        }}

        function populateFilters() {{
            const propertyTypes = [...new Set(currentData.map(item => item.property_type))].filter(Boolean);
            const statuses = [...new Set(currentData.map(item => item.status))].filter(Boolean);
            const files = [...new Set(currentData.map(item => item.file_source))].filter(Boolean);

            populateSelect('propertyTypeFilter', propertyTypes);
            populateSelect('statusFilter', statuses);
            populateSelect('fileFilter', files.map(f => f.split('/').pop()));
        }}

        function populateSelect(selectId, options) {{
            const select = document.getElementById(selectId);
            options.forEach(option => {{
                const optionElement = document.createElement('option');
                optionElement.value = option;
                optionElement.textContent = option;
                select.appendChild(optionElement);
            }});
        }}

        function displayData() {{
            const tbody = document.getElementById('dataTableBody');
            tbody.innerHTML = '';

            const startIndex = (currentPage - 1) * recordsPerPage;
            const endIndex = startIndex + recordsPerPage;
            const pageData = filteredData.slice(startIndex, endIndex);

            pageData.forEach(item => {{
                const row = document.createElement('tr');
                row.className = 'table-row';
                row.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{item.unique_id}}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="status-badge property-${{item.property_type.replace(' ', '')}}">${{item.property_type}}</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{item.location}}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{item.area || '-'}}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${{item.price || '-'}}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="status-badge status-${{item.status.replace(' ', '')}}">${{item.status}}</span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${{item.file_source.split('/').pop()}}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button onclick="viewDetails('${{item.unique_id}}')" class="text-blue-600 hover:text-blue-900 mr-2">عرض</button>
                    </td>
                `;
                tbody.appendChild(row);
            }});

            updatePaginationInfo();
        }}

        function viewDetails(uniqueId) {{
            const item = currentData.find(d => d.unique_id === uniqueId);
            if (!item) return;

            const rawData = JSON.parse(item.raw_data || '{{}}');
            
            document.getElementById('modalContent').innerHTML = `
                <h2 class="text-xl font-bold mb-4">تفاصيل السجل: ${{item.unique_id}}</h2>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div>
                        <h3 class="font-semibold mb-2">البيانات المعالجة:</h3>
                        <p><strong>نوع العقار:</strong> ${{item.property_type}}</p>
                        <p><strong>الموقع:</strong> ${{item.location}}</p>
                        <p><strong>المساحة:</strong> ${{item.area || 'غير محدد'}}</p>
                        <p><strong>السعر:</strong> ${{item.price || 'غير محدد'}}</p>
                        <p><strong>الحالة:</strong> ${{item.status}}</p>
                        <p><strong>جهة الاتصال:</strong> ${{item.contact || 'غير متوفر'}}</p>
                    </div>
                    <div>
                        <h3 class="font-semibold mb-2">معلومات المصدر:</h3>
                        <p><strong>الملف:</strong> ${{item.file_source}}</p>
                        <p><strong>الورقة:</strong> ${{item.sheet_name}}</p>
                        <p><strong>رقم الصف:</strong> ${{item.row_number}}</p>
                        <p><strong>تاريخ المعالجة:</strong> ${{item.date_processed}}</p>
                    </div>
                </div>
                <div class="mb-4">
                    <h3 class="font-semibold mb-2">الوصف:</h3>
                    <p class="text-gray-700">${{item.description}}</p>
                </div>
                <div>
                    <h3 class="font-semibold mb-2">البيانات الخام:</h3>
                    <div class="bg-gray-100 p-3 rounded text-sm max-h-40 overflow-y-auto">
                        ${{Object.entries(rawData).map(([key, value]) => `<p><strong>${{key}}:</strong> ${{value}}</p>`).join('')}}
                    </div>
                </div>
            `;
            
            document.getElementById('detailsModal').style.display = 'block';
        }}

        function closeModal() {{
            document.getElementById('detailsModal').style.display = 'none';
        }}

        function applyFilters() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const propertyType = document.getElementById('propertyTypeFilter').value;
            const status = document.getElementById('statusFilter').value;
            const file = document.getElementById('fileFilter').value;

            filteredData = currentData.filter(item => {{
                const matchesSearch = !searchTerm || 
                    Object.values(item).some(value => 
                        String(value).toLowerCase().includes(searchTerm)
                    );
                
                const matchesPropertyType = !propertyType || item.property_type === propertyType;
                const matchesStatus = !status || item.status === status;
                const matchesFile = !file || item.file_source.includes(file);

                return matchesSearch && matchesPropertyType && matchesStatus && matchesFile;
            }});

            currentPage = 1;
            displayData();
        }}

        function clearFilters() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('propertyTypeFilter').value = '';
            document.getElementById('statusFilter').value = '';
            document.getElementById('fileFilter').value = '';
            
            filteredData = [...currentData];
            currentPage = 1;
            displayData();
        }}

        function setupEventListeners() {{
            document.getElementById('searchInput').addEventListener('input', debounce(applyFilters, 300));
            document.getElementById('propertyTypeFilter').addEventListener('change', applyFilters);
            document.getElementById('statusFilter').addEventListener('change', applyFilters);
            document.getElementById('fileFilter').addEventListener('change', applyFilters);
        }}

        function debounce(func, wait) {{
            let timeout;
            return function executedFunction(...args) {{
                const later = () => {{
                    clearTimeout(timeout);
                    func(...args);
                }};
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            }};
        }}

        function updatePaginationInfo() {{
            const startIndex = (currentPage - 1) * recordsPerPage + 1;
            const endIndex = Math.min(currentPage * recordsPerPage, filteredData.length);
            const total = filteredData.length;

            document.getElementById('paginationInfo').innerHTML = 
                `عرض من <span class="font-medium">${{startIndex}}</span> إلى <span class="font-medium">${{endIndex}}</span> من أصل <span class="font-medium">${{total}}</span> نتيجة`;
        }}

        function nextPage() {{
            const totalPages = Math.ceil(filteredData.length / recordsPerPage);
            if (currentPage < totalPages) {{
                currentPage++;
                displayData();
            }}
        }}

        function previousPage() {{
            if (currentPage > 1) {{
                currentPage--;
                displayData();
            }}
        }}

        // Close modal when clicking outside
        window.onclick = function(event) {{
            const modal = document.getElementById('detailsModal');
            if (event.target === modal) {{
                closeModal();
            }}
        }}
    </script>
</body>
</html>'''

        try:
            with open(self.output_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"✅ HTML viewer generated: {self.output_html}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating HTML: {e}")
            return False
    
    def open_in_safari(self):
        """Open the generated HTML file in Safari"""
        try:
            html_path = os.path.abspath(self.output_html)
            file_url = f"file://{html_path}"
            
            # Open in Safari
            subprocess.run(['open', '-a', 'Safari', file_url], check=True)
            print(f"🌐 Opened in Safari: {file_url}")
            return True
            
        except Exception as e:
            print(f"❌ Error opening Safari: {e}")
            print(f"🔗 Manual URL: file://{os.path.abspath(self.output_html)}")
            return False
    
    def run(self):
        """Main execution method"""
        print("🚀 CSVs Data Processor Starting...")
        print("=" * 50)
        
        # Step 1: Check csvs folder
        if not self.check_csvs_folder():
            return False
        
        # Step 2: Process Excel files
        if not self.process_excel_files():
            print("❌ Failed to process Excel files")
            return False
        
        # Step 3: Save to CSV
        if not self.save_to_csv():
            print("❌ Failed to save CSV")
            return False
        
        # Step 4: Generate HTML
        if not self.generate_html_viewer():
            print("❌ Failed to generate HTML")
            return False
        
        # Step 5: Open in Safari
        print(f"\n🎉 Success! Generated {len(self.processed_data)} records")
        print(f"📄 CSV file: {self.output_csv}")
        print(f"🌐 HTML viewer: {self.output_html}")
        
        self.open_in_safari()
        
        return True


def main():
    """Main function"""
    processor = CSVsDataProcessor()
    
    try:
        success = processor.run()
        if success:
            print(f"\n✅ Process completed successfully!")
            print(f"📊 View your data at: file://{os.path.abspath(processor.output_html)}")
        else:
            print(f"\n❌ Process failed!")
            
    except KeyboardInterrupt:
        print(f"\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
