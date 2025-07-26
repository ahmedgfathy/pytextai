#!/usr/bin/env python3
"""
Excel Properties Data Analyzer and Visualizer
Creates interactive HTML dashboard for real estate properties data from Excel files
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime
import re

class ExcelPropertiesAnalyzer:
    def __init__(self, csvs_folder):
        self.csvs_folder = csvs_folder
        self.all_data = pd.DataFrame()
        self.analysis_results = {}
        
    def load_excel_files(self):
        """Load all Excel files from the csvs folder"""
        print("Loading Excel files...")
        excel_files = [f for f in os.listdir(self.csvs_folder) if f.endswith('.xlsx')]
        
        all_dataframes = []
        file_info = []
        
        for file in excel_files:
            try:
                file_path = os.path.join(self.csvs_folder, file)
                df = pd.read_excel(file_path)
                df['Source_File'] = file
                all_dataframes.append(df)
                file_info.append({
                    'filename': file,
                    'records': len(df),
                    'columns': len(df.columns)
                })
                print(f"✓ Loaded {file}: {len(df)} records")
            except Exception as e:
                print(f"✗ Error loading {file}: {e}")
        
        if all_dataframes:
            self.all_data = pd.concat(all_dataframes, ignore_index=True)
            print(f"\nTotal records loaded: {len(self.all_data)}")
            
        return file_info
    
    def clean_data(self):
        """Clean and standardize the data"""
        print("Cleaning data...")
        
        # Clean column names (remove tabs and extra spaces)
        self.all_data.columns = [col.replace('\t', '').strip() for col in self.all_data.columns]
        
        # Debug: Print cleaned columns
        print("Cleaned columns:", list(self.all_data.columns))
        
        # Convert price to numeric
        if 'Unit Price' in self.all_data.columns:
            self.all_data['Unit Price'] = pd.to_numeric(self.all_data['Unit Price'], errors='coerce')
        
        # Clean regions data
        if 'Regions' in self.all_data.columns:
            self.all_data['Regions'] = self.all_data['Regions'].fillna('غير محدد')
        
        # Clean property types
        if 'Property Type' in self.all_data.columns:
            self.all_data['Property Type'] = self.all_data['Property Type'].fillna('غير محدد')
        
        # Convert building size to numeric
        if 'Building' in self.all_data.columns:
            self.all_data['Building_Numeric'] = pd.to_numeric(self.all_data['Building'], errors='coerce')
        
        # Convert bedrooms to numeric
        if 'Bedroom' in self.all_data.columns:
            self.all_data['Bedroom_Numeric'] = pd.to_numeric(self.all_data['Bedroom'], errors='coerce')
        
        print("Data cleaning completed!")
    
    def analyze_data(self):
        """Perform comprehensive data analysis"""
        print("Analyzing data...")
        
        # Basic statistics
        total_properties = len(self.all_data)
        unique_regions = self.all_data['Regions'].nunique() if 'Regions' in self.all_data.columns else 0
        unique_categories = self.all_data['Property Category'].nunique() if 'Property Category' in self.all_data.columns else 0
        
        # Price analysis
        price_stats = {}
        if 'Unit Price' in self.all_data.columns:
            prices = self.all_data['Unit Price'].dropna()
            if len(prices) > 0:
                price_stats = {
                    'average': float(prices.mean()),
                    'median': float(prices.median()),
                    'min': float(prices.min()),
                    'max': float(prices.max()),
                    'std': float(prices.std())
                }
        
        # Regional analysis
        regional_data = []
        if 'Regions' in self.all_data.columns:
            region_counts = self.all_data['Regions'].value_counts().head(15)
            regional_data = [{'region': region, 'count': int(count)} for region, count in region_counts.items()]
        
        # Property type analysis
        property_types = []
        if 'Property Type' in self.all_data.columns:
            type_counts = self.all_data['Property Type'].value_counts().head(10)
            property_types = [{'type': ptype, 'count': int(count)} for ptype, count in type_counts.items()]
        
        # Category analysis
        categories = []
        if 'Property Category' in self.all_data.columns:
            cat_counts = self.all_data['Property Category'].value_counts()
            categories = [{'category': cat, 'count': int(count)} for cat, count in cat_counts.items()]
        
        # Building size analysis
        size_distribution = {}
        if 'Building_Numeric' in self.all_data.columns:
            sizes = self.all_data['Building_Numeric'].dropna()
            if len(sizes) > 0:
                size_distribution = {
                    'small_under_100': int(len(sizes[sizes < 100])),
                    'medium_100_200': int(len(sizes[(sizes >= 100) & (sizes < 200)])),
                    'large_200_300': int(len(sizes[(sizes >= 200) & (sizes < 300)])),
                    'xlarge_over_300': int(len(sizes[sizes >= 300]))
                }
        
        # Payment type analysis
        payment_types = []
        payment_col = 'Payment Type'
        if payment_col in self.all_data.columns:
            payment_counts = self.all_data[payment_col].value_counts()
            payment_types = [{'type': ptype, 'count': int(count)} for ptype, count in payment_counts.items()]
        
        # Bedroom distribution
        bedroom_dist = {}
        if 'Bedroom_Numeric' in self.all_data.columns:
            bedrooms = self.all_data['Bedroom_Numeric'].dropna()
            if len(bedrooms) > 0:
                bedroom_counts = bedrooms.value_counts().sort_index()
                bedroom_dist = {str(int(br)): int(count) for br, count in bedroom_counts.items() if not pd.isna(br)}
        
        # Price by region (top regions)
        price_by_region = []
        if 'Regions' in self.all_data.columns and 'Unit Price' in self.all_data.columns:
            top_regions = self.all_data['Regions'].value_counts().head(10).index
            for region in top_regions:
                region_data = self.all_data[self.all_data['Regions'] == region]
                prices = region_data['Unit Price'].dropna()
                if len(prices) > 0:
                    price_by_region.append({
                        'region': region,
                        'avg_price': float(prices.mean()),
                        'median_price': float(prices.median()),
                        'count': len(prices)
                    })
        
        self.analysis_results = {
            'summary': {
                'total_properties': total_properties,
                'unique_regions': unique_regions,
                'unique_categories': unique_categories,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'price_stats': price_stats,
            'regional_data': regional_data,
            'property_types': property_types,
            'categories': categories,
            'size_distribution': size_distribution,
            'payment_types': payment_types,
            'bedroom_distribution': bedroom_dist,
            'price_by_region': price_by_region
        }
        
        print(f"Analysis completed! Found {total_properties} properties across {unique_regions} regions")
        return self.analysis_results
    
    def prepare_data_for_json(self):
        """Prepare data for JSON serialization"""
        # Create a copy of the data and convert all columns to strings to avoid JSON serialization issues
        data_copy = self.all_data.copy()
        
        # Convert all columns to string type and handle NaN values
        for col in data_copy.columns:
            data_copy[col] = data_copy[col].astype(str).replace('nan', '').replace('NaT', '')
        
        # Convert to list of dictionaries
        records = data_copy.to_dict('records')
        
        # Further clean the records
        cleaned_records = []
        for record in records:
            cleaned_record = {}
            for key, value in record.items():
                # Clean the key and value
                clean_key = str(key).replace('\t', '').strip()
                clean_value = str(value).strip() if value and str(value) != 'nan' else ''
                cleaned_record[clean_key] = clean_value
            cleaned_records.append(cleaned_record)
        
        return cleaned_records
    
    def generate_html_dashboard(self, output_file='excel_properties_dashboard.html'):
        """Generate beautiful HTML dashboard"""
        
        # Debug: Print analysis results summary
        print("=" * 50)
        print("DEBUG: Analysis results before HTML generation:")
        print(f"Regional data: {len(self.analysis_results.get('regional_data', []))} items")
        print(f"Property types: {len(self.analysis_results.get('property_types', []))} items")
        print(f"Categories: {len(self.analysis_results.get('categories', []))} items")
        print(f"Size distribution: {len(self.analysis_results.get('size_distribution', {}))} items")
        print("=" * 50)
        
        html_content = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحليل العقارات - Excel Properties Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/js/all.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Cairo', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            direction: rtl;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            padding: 40px 0;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .stat-card {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-left: 5px solid #667eea;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        }}
        
        .stat-card .icon {{
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 15px;
        }}
        
        .stat-card .number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }}
        
        .stat-card .label {{
            font-size: 1rem;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        
        .chart-container {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .chart-title {{
            font-size: 1.5rem;
            font-weight: bold;
            margin-bottom: 20px;
            color: #333;
            text-align: center;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .chart-canvas {{
            max-height: 400px;
        }}
        
        .data-table {{
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-top: 30px;
        }}
        
        .table-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        
        .table-content {{
            max-height: 400px;
            overflow-y: auto;
            padding: 20px;
        }}
        
        .data-row {{
            display: flex;
            justify-content: space-between;
            padding: 15px;
            border-bottom: 1px solid #eee;
            transition: background-color 0.3s ease;
        }}
        
        .data-row:hover {{
            background-color: #f8f9fa;
        }}
        
        .data-label {{
            font-weight: bold;
            color: #333;
        }}
        
        .data-value {{
            color: #667eea;
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            color: white;
            margin-top: 50px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .complete-data-table {{
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-top: 30px;
        }}
        
        .table-controls {{
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            align-items: center;
            justify-content: space-between;
        }}
        
        .search-container {{
            position: relative;
            flex: 1;
            min-width: 250px;
        }}
        
        .search-container i {{
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #666;
        }}
        
        .search-container input {{
            width: 100%;
            padding: 12px 45px 12px 15px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
            transition: border-color 0.3s ease;
        }}
        
        .search-container input:focus {{
            border-color: #667eea;
        }}
        
        .filter-container {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .filter-container select {{
            padding: 8px 15px;
            border: 2px solid #e9ecef;
            border-radius: 20px;
            background: white;
            font-size: 14px;
            outline: none;
            cursor: pointer;
        }}
        
        .table-info {{
            font-size: 14px;
            color: #666;
            font-weight: bold;
        }}
        
        .table-scroll {{
            max-height: 600px;
            overflow: auto;
            border-bottom: 2px solid #e9ecef;
        }}
        
        #propertiesTable {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        
        #propertiesTable th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 8px;
            text-align: center;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 10;
            border-right: 1px solid rgba(255,255,255,0.2);
        }}
        
        #propertiesTable td {{
            padding: 12px 8px;
            text-align: center;
            border-bottom: 1px solid #e9ecef;
            border-right: 1px solid #e9ecef;
            vertical-align: middle;
        }}
        
        #propertiesTable tbody tr:hover {{
            background-color: #f8f9fa;
        }}
        
        #propertiesTable tbody tr:nth-child(even) {{
            background-color: #fdfdfd;
        }}
        
        .description-cell {{
            max-width: 200px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            cursor: pointer;
        }}
        
        .description-cell:hover {{
            white-space: normal;
            background: #f0f0f0;
            position: relative;
            z-index: 5;
        }}
        
        .price-cell {{
            font-weight: bold;
            color: #28a745;
        }}
        
        .pagination {{
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 15px;
            background: #f8f9fa;
        }}
        
        .pagination button {{
            padding: 8px 16px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
        }}
        
        .pagination button:hover:not(:disabled) {{
            background: #667eea;
            color: white;
        }}
        
        .pagination button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        
        .pagination select {{
            padding: 8px 15px;
            border: 2px solid #e9ecef;
            border-radius: 20px;
            background: white;
            cursor: pointer;
        }}
        
        #pageInfo {{
            font-weight: bold;
            color: #333;
        }}
        
        .loading {{
            display: none;
            text-align: center;
            color: white;
            font-size: 1.2rem;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .chart-container, .stat-card {{
            animation: fadeIn 0.6s ease-out;
        }}
        
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .stat-card .number {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><i class="fas fa-building"></i> لوحة تحليل العقارات</h1>
            <p>تحليل شامل لبيانات العقارات من ملفات Excel</p>
            <p style="font-size: 0.9rem; margin-top: 10px;">تم التحديث: {self.analysis_results['summary']['analysis_date']}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon"><i class="fas fa-home"></i></div>
                <div class="number">{self.analysis_results['summary']['total_properties']:,}</div>
                <div class="label">إجمالي العقارات</div>
            </div>
            <div class="stat-card">
                <div class="icon"><i class="fas fa-map-marker-alt"></i></div>
                <div class="number">{self.analysis_results['summary']['unique_regions']}</div>
                <div class="label">المناطق المختلفة</div>
            </div>
            <div class="stat-card">
                <div class="icon"><i class="fas fa-tags"></i></div>
                <div class="number">{self.analysis_results['summary']['unique_categories']}</div>
                <div class="label">فئات العقارات</div>
            </div>
            <div class="stat-card">
                <div class="icon"><i class="fas fa-dollar-sign"></i></div>
                <div class="number">{self.analysis_results['price_stats'].get('average', 0):,.0f}</div>
                <div class="label">متوسط السعر</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">توزيع العقارات حسب المنطقة</div>
                <canvas id="regionsChart" class="chart-canvas"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">أنواع العقارات</div>
                <canvas id="propertyTypesChart" class="chart-canvas"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">فئات العقارات</div>
                <canvas id="categoriesChart" class="chart-canvas"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">توزيع أحجام العقارات</div>
                <canvas id="sizesChart" class="chart-canvas"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">أنواع الدفع</div>
                <canvas id="paymentChart" class="chart-canvas"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">توزيع غرف النوم</div>
                <canvas id="bedroomsChart" class="chart-canvas"></canvas>
            </div>
        </div>
        
        <div class="data-table">
            <div class="table-header">
                <h2><i class="fas fa-chart-bar"></i> متوسط الأسعار حسب المنطقة</h2>
            </div>
            <div class="table-content">
                <div id="priceByRegionTable"></div>
            </div>
        </div>
        
        <!-- Complete Data Table -->
        <div class="complete-data-table">
            <div class="table-header">
                <h2><i class="fas fa-table"></i> جدول البيانات الكاملة - جميع العقارات ({self.analysis_results['summary']['total_properties']:,} عقار)</h2>
                <p style="margin-top: 10px; font-size: 0.9rem;">يمكنك البحث والفلترة والتصفح عبر جميع السجلات</p>
            </div>
            <div class="table-controls">
                <div class="search-container">
                    <i class="fas fa-search"></i>
                    <input type="text" id="searchInput" placeholder="البحث في جميع البيانات...">
                </div>
                <div class="filter-container">
                    <select id="regionFilter">
                        <option value="">جميع المناطق</option>
                    </select>
                    <select id="typeFilter">
                        <option value="">جميع الأنواع</option>
                    </select>
                    <select id="categoryFilter">
                        <option value="">جميع الفئات</option>
                    </select>
                </div>
                <div class="table-info">
                    <span id="tableInfo">عرض جميع السجلات</span>
                </div>
            </div>
            <div class="table-scroll">
                <table id="propertiesTable">
                    <thead>
                        <tr>
                            <th>اسم العقار</th>
                            <th>المنطقة</th>
                            <th>الفئة</th>
                            <th>النوع</th>
                            <th>المساحة</th>
                            <th>غرف النوم</th>
                            <th>الحمامات</th>
                            <th>الطابق</th>
                            <th>السعر</th>
                            <th>طريقة الدفع</th>
                            <th>المالك</th>
                            <th>الهاتف</th>
                            <th>التشطيب</th>
                            <th>الوصف</th>
                        </tr>
                    </thead>
                    <tbody id="propertiesTableBody">
                    </tbody>
                </table>
            </div>
            <div class="pagination">
                <button id="prevPage"><i class="fas fa-chevron-right"></i> السابق</button>
                <span id="pageInfo">الصفحة 1</span>
                <button id="nextPage">التالي <i class="fas fa-chevron-left"></i></button>
                <select id="pageSize">
                    <option value="50">50 سجل</option>
                    <option value="100">100 سجل</option>
                    <option value="200">200 سجل</option>
                    <option value="500">500 سجل</option>
                </select>
            </div>
        </div>
        
        <div class="footer">
            <p><i class="fas fa-chart-line"></i> تم إنشاء هذا التقرير بواسطة محلل العقارات الذكي</p>
            <p style="font-size: 0.9rem; margin-top: 10px;">Excel Properties Analyzer</p>
        </div>
    </div>

    <script>
        // Data from Python analysis
        const analysisData = {json.dumps(self.analysis_results, ensure_ascii=False, indent=2)};
        
        // Debug: Log the data that was loaded
        console.log('=== DASHBOARD DATA DEBUGGING ===');
        console.log('Analysis data loaded:', analysisData);
        console.log('Regional data count:', analysisData.regional_data ? analysisData.regional_data.length : 0);
        console.log('Property types count:', analysisData.property_types ? analysisData.property_types.length : 0);
        console.log('Categories count:', analysisData.categories ? analysisData.categories.length : 0);
        console.log('=== END DEBUGGING ===');
        
        // Initialize when DOM is ready
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('DOM loaded, initializing dashboard...');
            console.log('Analysis data loaded:', analysisData);
            
            // Debug: Log the data that was loaded
            console.log('=== DASHBOARD DATA DEBUGGING ===');
            console.log('Analysis data loaded:', analysisData);
            console.log('Regional data count:', analysisData.regional_data ? analysisData.regional_data.length : 0);
            console.log('Property types count:', analysisData.property_types ? analysisData.property_types.length : 0);
            console.log('Categories count:', analysisData.categories ? analysisData.categories.length : 0);
            console.log('=== END DEBUGGING ===');
            
            // Chart configuration
            Chart.defaults.font.family = 'Cairo, sans-serif';
            Chart.defaults.font.size = 12;
            
            // Initialize charts FIRST
            createCharts();
            
            // Then initialize table
            initializeTable();
        }});
        
        function createCharts() {{
            console.log('Creating charts...');
            
            // Colors palette
            const colors = [
                '#667eea', '#764ba2', '#f093fb', '#f5576c',
                '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
                '#ffecd2', '#fcb69f', '#a8edea', '#fed6e3'
            ];
        
        // Regions Chart
        if (analysisData.regional_data && analysisData.regional_data.length > 0) {{
            const regionsCtx = document.getElementById('regionsChart').getContext('2d');
            new Chart(regionsCtx, {{
                type: 'bar',
                data: {{
                    labels: analysisData.regional_data.map(item => item.region),
                    datasets: [{{
                        label: 'عدد العقارات',
                        data: analysisData.regional_data.map(item => item.count),
                        backgroundColor: colors.slice(0, analysisData.regional_data.length),
                        borderColor: colors.slice(0, analysisData.regional_data.length),
                        borderWidth: 2,
                        borderRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.parsed.y.toLocaleString() + ' عقار';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            ticks: {{
                                callback: function(value) {{
                                    return value.toLocaleString();
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Property Types Chart
        if (analysisData.property_types && analysisData.property_types.length > 0) {{
            const typesCtx = document.getElementById('propertyTypesChart').getContext('2d');
            new Chart(typesCtx, {{
                type: 'doughnut',
                data: {{
                    labels: analysisData.property_types.map(item => item.type),
                    datasets: [{{
                        data: analysisData.property_types.map(item => item.count),
                        backgroundColor: colors.slice(0, analysisData.property_types.length),
                        borderWidth: 3,
                        borderColor: '#fff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                padding: 20,
                                font: {{ size: 11 }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.label + ': ' + context.parsed.toLocaleString() + ' عقار';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Categories Chart
        if (analysisData.categories && analysisData.categories.length > 0) {{
            const categoriesCtx = document.getElementById('categoriesChart').getContext('2d');
            new Chart(categoriesCtx, {{
                type: 'pie',
                data: {{
                    labels: analysisData.categories.map(item => item.category),
                    datasets: [{{
                        data: analysisData.categories.map(item => item.count),
                        backgroundColor: colors.slice(0, analysisData.categories.length),
                        borderWidth: 3,
                        borderColor: '#fff'
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{
                                padding: 20,
                                font: {{ size: 11 }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.label + ': ' + context.parsed.toLocaleString() + ' عقار';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // Sizes Chart
        if (analysisData.size_distribution && Object.keys(analysisData.size_distribution).length > 0) {{
            const sizesCtx = document.getElementById('sizesChart').getContext('2d');
            const sizeLabels = ['أقل من 100م²', '100-200م²', '200-300م²', 'أكثر من 300م²'];
            const sizeData = [
                analysisData.size_distribution.small_under_100 || 0,
                analysisData.size_distribution.medium_100_200 || 0,
                analysisData.size_distribution.large_200_300 || 0,
                analysisData.size_distribution.xlarge_over_300 || 0
            ];
            
            new Chart(sizesCtx, {{
                type: 'bar',
                data: {{
                    labels: sizeLabels,
                    datasets: [{{
                        label: 'عدد العقارات',
                        data: sizeData,
                        backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#f5576c'],
                        borderRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        }}
        
        // Payment Types Chart
        if (analysisData.payment_types && analysisData.payment_types.length > 0) {{
            const paymentCtx = document.getElementById('paymentChart').getContext('2d');
            new Chart(paymentCtx, {{
                type: 'doughnut',
                data: {{
                    labels: analysisData.payment_types.map(item => item.type || 'غير محدد'),
                    datasets: [{{
                        data: analysisData.payment_types.map(item => item.count),
                        backgroundColor: colors.slice(0, analysisData.payment_types.length)
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{
                            position: 'bottom'
                        }}
                    }}
                }}
            }});
        }}
        
        // Bedrooms Chart
        if (analysisData.bedroom_distribution && Object.keys(analysisData.bedroom_distribution).length > 0) {{
            const bedroomsCtx = document.getElementById('bedroomsChart').getContext('2d');
            const bedroomLabels = Object.keys(analysisData.bedroom_distribution).sort((a, b) => parseInt(a) - parseInt(b));
            const bedroomData = bedroomLabels.map(key => analysisData.bedroom_distribution[key]);
            
            new Chart(bedroomsCtx, {{
                type: 'bar',
                data: {{
                    labels: bedroomLabels.map(label => label + ' غرف'),
                    datasets: [{{
                        label: 'عدد العقارات',
                        data: bedroomData,
                        backgroundColor: '#667eea',
                        borderRadius: 8
                    }}]
                }},
                options: {{
                    responsive: true,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        y: {{
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        }}
        
        // Price by Region Table
        if (analysisData.price_by_region && analysisData.price_by_region.length > 0) {{
            const tableContainer = document.getElementById('priceByRegionTable');
            let tableHTML = '';
            
            analysisData.price_by_region.forEach(item => {{
                tableHTML += `
                    <div class="data-row">
                        <div class="data-label">${{item.region}}</div>
                        <div class="data-value">${{item.avg_price.toLocaleString()}} جنيه</div>
                    </div>
                `;
            }});
            
            tableContainer.innerHTML = tableHTML;
        }}
        
        // Animation on scroll
        const observerOptions = {{
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        }};
        
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }}
            }});
        }}, observerOptions);
        
        document.querySelectorAll('.chart-container, .stat-card').forEach(el => {{
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        }});
        
            }} catch (error) {{
                console.error('Error creating charts:', error);
            }}
        }}
        
        // Complete Data Table functionality
        let allProperties = {json.dumps(self.prepare_data_for_json(), ensure_ascii=False)};
        let filteredProperties = [...allProperties];
        let currentPage = 1;
        let pageSize = 50;
        
        // Initialize table
        function initializeTable() {{
            populateFilters();
            updateTable();
            setupEventListeners();
        }}
        
        // Populate filter dropdowns
        function populateFilters() {{
            const regions = [...new Set(allProperties.map(p => p.Regions).filter(r => r))];
            const types = [...new Set(allProperties.map(p => p['Property Type']).filter(t => t))];
            const categories = [...new Set(allProperties.map(p => p['Property Category']).filter(c => c))];
            
            populateSelect('regionFilter', regions);
            populateSelect('typeFilter', types);
            populateSelect('categoryFilter', categories);
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
        
        // Filter properties
        function filterProperties() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const regionFilter = document.getElementById('regionFilter').value;
            const typeFilter = document.getElementById('typeFilter').value;
            const categoryFilter = document.getElementById('categoryFilter').value;
            
            filteredProperties = allProperties.filter(property => {{
                const matchesSearch = !searchTerm || 
                    Object.values(property).some(value => 
                        String(value).toLowerCase().includes(searchTerm)
                    );
                const matchesRegion = !regionFilter || property.Regions === regionFilter;
                const matchesType = !typeFilter || property['Property Type'] === typeFilter;
                const matchesCategory = !categoryFilter || property['Property Category'] === categoryFilter;
                
                return matchesSearch && matchesRegion && matchesType && matchesCategory;
            }});
            
            currentPage = 1;
            updateTable();
        }}
        
        // Update table display
        function updateTable() {{
            const startIndex = (currentPage - 1) * pageSize;
            const endIndex = startIndex + pageSize;
            const pageProperties = filteredProperties.slice(startIndex, endIndex);
            
            const tbody = document.getElementById('propertiesTableBody');
            tbody.innerHTML = '';
            
            pageProperties.forEach(property => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${{property['Property Name'] || ''}}</td>
                    <td>${{property.Regions || ''}}</td>
                    <td>${{property['Property Category'] || ''}}</td>
                    <td>${{property['Property Type'] || ''}}</td>
                    <td>${{property.Building || ''}}</td>
                    <td>${{property.Bedroom || ''}}</td>
                    <td>${{property.Bathroom || ''}}</td>
                    <td>${{property['Floor No.'] || ''}}</td>
                    <td class="price-cell">${{formatPrice(property['Unit Price'])}}</td>
                    <td>${{property['Payment Type'] || ''}}</td>
                    <td>${{property['Name'] || ''}}</td>
                    <td>${{property['Mobile No'] || ''}}</td>
                    <td>${{property['Finished'] || ''}}</td>
                    <td class="description-cell" title="${{property.Description || ''}}">${{truncateText(property.Description || '', 50)}}</td>
                `;
                tbody.appendChild(row);
            }});
            
            updateTableInfo();
            updatePaginationControls();
        }}
        
        // Helper functions
        function formatPrice(price) {{
            if (!price || isNaN(price)) return '';
            return Number(price).toLocaleString() + ' جنيه';
        }}
        
        function truncateText(text, maxLength) {{
            if (text.length <= maxLength) return text;
            return text.substring(0, maxLength) + '...';
        }}
        
        function updateTableInfo() {{
            const totalFiltered = filteredProperties.length;
            const totalAll = allProperties.length;
            const startIndex = (currentPage - 1) * pageSize + 1;
            const endIndex = Math.min(currentPage * pageSize, totalFiltered);
            
            document.getElementById('tableInfo').textContent = 
                `عرض ${{startIndex}}-${{endIndex}} من ${{totalFiltered}} سجل (إجمالي: ${{totalAll}})`;
        }}
        
        function updatePaginationControls() {{
            const totalPages = Math.ceil(filteredProperties.length / pageSize);
            
            document.getElementById('prevPage').disabled = currentPage === 1;
            document.getElementById('nextPage').disabled = currentPage === totalPages;
            document.getElementById('pageInfo').textContent = `الصفحة ${{currentPage}} من ${{totalPages}}`;
        }}
        
        // Event listeners
        function setupEventListeners() {{
            document.getElementById('searchInput').addEventListener('input', filterProperties);
            document.getElementById('regionFilter').addEventListener('change', filterProperties);
            document.getElementById('typeFilter').addEventListener('change', filterProperties);
            document.getElementById('categoryFilter').addEventListener('change', filterProperties);
            
            document.getElementById('prevPage').addEventListener('click', () => {{
                if (currentPage > 1) {{
                    currentPage--;
                    updateTable();
                }}
            }});
            
            document.getElementById('nextPage').addEventListener('click', () => {{
                const totalPages = Math.ceil(filteredProperties.length / pageSize);
                if (currentPage < totalPages) {{
                    currentPage++;
                    updateTable();
                }}
            }});
            
            document.getElementById('pageSize').addEventListener('change', (e) => {{
                pageSize = parseInt(e.target.value);
                currentPage = 1;
                updateTable();
            }});
        }}
        
            // Initialize table
            initializeTable();
            
        }}); // End of DOMContentLoaded

    </script>
</body>
</html>'''
        
        # Write HTML file
        print(f"Writing HTML file: {output_file}")
        print(f"HTML content length: {len(html_content)} characters")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Verify the file was written correctly
        with open(output_file, 'r', encoding='utf-8') as f:
            written_content = f.read()
            print(f"File written successfully: {len(written_content)} characters")
            
            # Check if the JSON data is in the file
            if 'regional_data' in written_content:
                print("✓ Regional data found in written file")
            else:
                print("✗ Regional data NOT found in written file")
        
        print(f"HTML dashboard generated: {output_file}")
        return output_file

def main():
    # Initialize analyzer
    csvs_folder = '/Users/ahmedgomaa/Documents/pytextai/csvs'
    analyzer = ExcelPropertiesAnalyzer(csvs_folder)
    
    # Load and analyze data
    print("🏠 Excel Properties Analyzer Starting...")
    print("=" * 50)
    
    file_info = analyzer.load_excel_files()
    
    if len(analyzer.all_data) == 0:
        print("❌ No data found in Excel files!")
        return
    
    analyzer.clean_data()
    results = analyzer.analyze_data()
    
    # Generate HTML dashboard
    output_file = analyzer.generate_html_dashboard()
    
    print("=" * 50)
    print("✅ Analysis completed successfully!")
    print(f"📊 Dashboard saved as: {output_file}")
    print(f"📈 Total properties analyzed: {results['summary']['total_properties']:,}")
    print(f"🗺️  Regions covered: {results['summary']['unique_regions']}")
    
    return output_file

if __name__ == "__main__":
    main()
