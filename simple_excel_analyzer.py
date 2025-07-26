#!/usr/bin/env python3
"""
Simple Excel Properties Dashboard - Testing Version
"""

import pandas as pd
import numpy as np
import os
import json
from datetime import datetime

class SimpleExcelAnalyzer:
    def __init__(self, csvs_folder):
        self.csvs_folder = csvs_folder
        self.all_data = pd.DataFrame()
        self.analysis_results = {}
        
    def load_excel_files(self):
        """Load all Excel files from the csvs folder"""
        print("Loading Excel files...")
        excel_files = [f for f in os.listdir(self.csvs_folder) if f.endswith('.xlsx')]
        
        all_dataframes = []
        for file in excel_files:
            try:
                file_path = os.path.join(self.csvs_folder, file)
                df = pd.read_excel(file_path)
                df['Source_File'] = file
                all_dataframes.append(df)
                print(f"✓ Loaded {file}: {len(df)} records")
            except Exception as e:
                print(f"✗ Error loading {file}: {e}")
        
        if all_dataframes:
            self.all_data = pd.concat(all_dataframes, ignore_index=True)
            print(f"Total records loaded: {len(self.all_data)}")
            
    def clean_data(self):
        """Clean and standardize the data"""
        print("Cleaning data...")
        
        # Clean column names (remove tabs and extra spaces)
        self.all_data.columns = [col.replace('\t', '').strip() for col in self.all_data.columns]
        
        # Clean regions data
        if 'Regions' in self.all_data.columns:
            self.all_data['Regions'] = self.all_data['Regions'].fillna('غير محدد')
        
        # Clean property types
        if 'Property Type' in self.all_data.columns:
            self.all_data['Property Type'] = self.all_data['Property Type'].fillna('غير محدد')
            
        print("Data cleaning completed!")
    
    def analyze_data(self):
        """Perform comprehensive data analysis"""
        print("Analyzing data...")
        
        # Basic statistics
        total_properties = len(self.all_data)
        unique_regions = self.all_data['Regions'].nunique() if 'Regions' in self.all_data.columns else 0
        unique_categories = self.all_data['Property Category'].nunique() if 'Property Category' in self.all_data.columns else 0
        
        # Regional analysis
        regional_data = []
        if 'Regions' in self.all_data.columns:
            region_counts = self.all_data['Regions'].value_counts().head(10)
            regional_data = [{'region': region, 'count': int(count)} for region, count in region_counts.items()]
        
        # Property type analysis
        property_types = []
        if 'Property Type' in self.all_data.columns:
            type_counts = self.all_data['Property Type'].value_counts().head(10)
            property_types = [{'type': ptype, 'count': int(count)} for ptype, count in type_counts.items()]
        
        # Category analysis
        categories = []
        if 'Property Category' in self.all_data.columns:
            cat_counts = self.all_data['Property Category'].value_counts().head(10)
            categories = [{'category': cat, 'count': int(count)} for cat, count in cat_counts.items()]
        
        self.analysis_results = {
            'summary': {
                'total_properties': total_properties,
                'unique_regions': unique_regions,
                'unique_categories': unique_categories,
                'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'regional_data': regional_data,
            'property_types': property_types,
            'categories': categories
        }
        
        print(f"Analysis completed! Found {total_properties} properties across {unique_regions} regions")
        return self.analysis_results
    
    def generate_simple_html(self, output_file='simple_dashboard.html'):
        """Generate simple HTML dashboard"""
        html_content = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة تحليل العقارات البسيطة</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #667eea;
        }}
        
        .stat-number {{
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
        }}
        
        .chart-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #eee;
        }}
        
        .chart-title {{
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 15px;
            text-align: center;
            color: #333;
        }}
        
        #status {{
            background: #e3f2fd;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
            border: 1px solid #2196f3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 لوحة تحليل العقارات</h1>
            <p>تحليل شامل لبيانات العقارات من ملفات Excel</p>
        </div>
        
        <div id="status">جاري التحميل...</div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{self.analysis_results['summary']['total_properties']:,}</div>
                <div class="stat-label">إجمالي العقارات</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.analysis_results['summary']['unique_regions']}</div>
                <div class="stat-label">المناطق المختلفة</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.analysis_results['summary']['unique_categories']}</div>
                <div class="stat-label">فئات العقارات</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">توزيع العقارات حسب المنطقة</div>
                <canvas id="regionsChart" style="max-height: 300px;"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">أنواع العقارات</div>
                <canvas id="typesChart" style="max-height: 300px;"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">فئات العقارات</div>
                <canvas id="categoriesChart" style="max-height: 300px;"></canvas>
            </div>
        </div>
    </div>

    <script>
        // Data from Python analysis
        const analysisData = {json.dumps(self.analysis_results, ensure_ascii=False, indent=2)};
        
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('DOM loaded - creating charts...');
            console.log('Analysis data:', analysisData);
            
            document.getElementById('status').textContent = 'تم تحميل البيانات بنجاح - جاري إنشاء الرسوم البيانية...';
            
            // Colors palette
            const colors = [
                '#667eea', '#764ba2', '#f093fb', '#f5576c',
                '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
                '#ffecd2', '#fcb69f', '#a8edea', '#fed6e3'
            ];
            
            try {{
                // Regions Chart
                if (analysisData.regional_data && analysisData.regional_data.length > 0) {{
                    console.log('Creating regions chart...');
                    const regionsCtx = document.getElementById('regionsChart').getContext('2d');
                    new Chart(regionsCtx, {{
                        type: 'bar',
                        data: {{
                            labels: analysisData.regional_data.map(item => item.region),
                            datasets: [{{
                                label: 'عدد العقارات',
                                data: analysisData.regional_data.map(item => item.count),
                                backgroundColor: colors.slice(0, analysisData.regional_data.length),
                                borderWidth: 2,
                                borderRadius: 5
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
                    console.log('Regions chart created');
                }} else {{
                    console.log('No regional data available');
                }}
                
                // Property Types Chart
                if (analysisData.property_types && analysisData.property_types.length > 0) {{
                    console.log('Creating types chart...');
                    const typesCtx = document.getElementById('typesChart').getContext('2d');
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
                                legend: {{ position: 'bottom' }}
                            }}
                        }}
                    }});
                    console.log('Types chart created');
                }} else {{
                    console.log('No property types data available');
                }}
                
                // Categories Chart
                if (analysisData.categories && analysisData.categories.length > 0) {{
                    console.log('Creating categories chart...');
                    const categoriesCtx = document.getElementById('categoriesChart').getContext('2d');
                    new Chart(categoriesCtx, {{
                        type: 'pie',
                        data: {{
                            labels: analysisData.categories.map(item => item.category),
                            datasets: [{{
                                data: analysisData.categories.map(item => item.count),
                                backgroundColor: colors
                            }}]
                        }},
                        options: {{
                            responsive: true,
                            plugins: {{
                                legend: {{ position: 'right' }}
                            }}
                        }}
                    }});
                    console.log('Categories chart created');
                }} else {{
                    console.log('No categories data available');
                }}
                
                document.getElementById('status').textContent = '✅ تم إنشاء جميع الرسوم البيانية بنجاح!';
                
            }} catch (error) {{
                console.error('Error creating charts:', error);
                document.getElementById('status').textContent = 'خطأ في إنشاء الرسوم البيانية: ' + error.message;
            }}
        }});
    </script>
</body>
</html>'''
        
        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Simple HTML dashboard generated: {output_file}")
        return output_file

if __name__ == "__main__":
    print("🏠 Simple Excel Properties Analyzer Starting...")
    print("=" * 50)
    
    # Create analyzer
    analyzer = SimpleExcelAnalyzer('csvs')
    
    # Load and analyze data
    analyzer.load_excel_files()
    analyzer.clean_data()
    results = analyzer.analyze_data()
    
    # Generate HTML dashboard
    output_file = analyzer.generate_simple_html()
    
    print("=" * 50)
    print("✅ Simple analysis completed successfully!")
    print(f"📊 Dashboard saved as: {output_file}")
    print(f"📈 Total properties analyzed: {results['summary']['total_properties']:,}")
    print(f"🗺️  Regions covered: {results['summary']['unique_regions']}")
