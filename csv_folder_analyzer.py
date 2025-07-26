import pandas as pd
import json
import os
from pathlib import Path
import numpy as np

class CSVFolderAnalyzer:
    def __init__(self, csv_folder_path):
        self.csv_folder_path = Path(csv_folder_path)
        self.data = None
        self.analysis_results = {}
        
    def load_excel_files(self):
        """Load all Excel files from the csvs folder"""
        all_data = []
        excel_files = list(self.csv_folder_path.glob("*.xlsx"))
        
        print(f"Found {len(excel_files)} Excel files in {self.csv_folder_path}")
        
        for file_path in excel_files:
            try:
                print(f"Loading: {file_path.name}")
                df = pd.read_excel(file_path)
                df['source_file'] = file_path.name
                all_data.append(df)
                print(f"  Loaded {len(df)} rows from {file_path.name}")
            except Exception as e:
                print(f"Error loading {file_path.name}: {str(e)}")
                continue
        
        if all_data:
            self.data = pd.concat(all_data, ignore_index=True)
            print(f"\\nTotal records loaded: {len(self.data)}")
            print(f"Columns: {list(self.data.columns)}")
            return True
        else:
            print("No data loaded!")
            return False
    
    def analyze_data(self):
        """Analyze the loaded data"""
        if self.data is None:
            print("No data to analyze!")
            return False
        
        print("\\nAnalyzing data...")
        
        # Basic statistics
        self.analysis_results['total_records'] = len(self.data)
        self.analysis_results['total_columns'] = len(self.data.columns)
        self.analysis_results['source_files'] = self.data['source_file'].unique().tolist()
        
        # Identify potential location and property type columns
        location_columns = []
        property_type_columns = []
        numeric_columns = []
        
        for col in self.data.columns:
            if col == 'source_file':
                continue
                
            # Check if column contains location-like data
            if any(keyword in col.lower() for keyword in ['region', 'area', 'location', 'city', 'district', 'منطقة']):
                location_columns.append(col)
            
            # Check if column contains property type data
            elif any(keyword in col.lower() for keyword in ['type', 'category', 'نوع']):
                property_type_columns.append(col)
            
            # Check if column is numeric
            elif pd.api.types.is_numeric_dtype(self.data[col]):
                numeric_columns.append(col)
        
        print(f"Location columns found: {location_columns}")
        print(f"Property type columns found: {property_type_columns}")
        print(f"Numeric columns found: {numeric_columns}")
        
        # Analyze by source file
        file_analysis = {}
        for file in self.analysis_results['source_files']:
            file_data = self.data[self.data['source_file'] == file]
            file_analysis[file] = len(file_data)
        
        self.analysis_results['records_by_file'] = file_analysis
        
        # Analyze first few columns for patterns
        column_analysis = {}
        for i, col in enumerate(self.data.columns[:10]):  # Analyze first 10 columns
            if col == 'source_file':
                continue
                
            col_data = self.data[col].dropna()
            if len(col_data) > 0:
                unique_values = col_data.nunique()
                top_values = col_data.value_counts().head(10).to_dict()
                
                column_analysis[col] = {
                    'unique_count': unique_values,
                    'total_records': len(col_data),
                    'top_values': top_values,
                    'data_type': str(col_data.dtype)
                }
        
        self.analysis_results['column_analysis'] = column_analysis
        
        # Try to create meaningful charts based on available data
        self.create_chart_data()
        
        return True
    
    def create_chart_data(self):
        """Create chart data based on available columns"""
        charts_data = {}
        
        # Chart 1: Records by source file
        charts_data['files_chart'] = {
            'labels': list(self.analysis_results['records_by_file'].keys()),
            'data': list(self.analysis_results['records_by_file'].values()),
            'title': 'توزيع البيانات حسب الملف',
            'colors': ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe']
        }
        
        # Chart 2: Top values from the most diverse column
        best_column = None
        best_diversity = 0
        
        for col, info in self.analysis_results['column_analysis'].items():
            diversity_score = min(info['unique_count'], 20)  # Cap at 20 for visualization
            if diversity_score > best_diversity and info['unique_count'] > 1:
                best_diversity = diversity_score
                best_column = col
        
        if best_column:
            top_values = self.analysis_results['column_analysis'][best_column]['top_values']
            charts_data['top_values_chart'] = {
                'labels': list(top_values.keys())[:10],
                'data': list(top_values.values())[:10],
                'title': f'أهم القيم في عمود: {best_column}',
                'colors': ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dda0dd', '#98d8c8', '#f7dc6f', '#bb8fce', '#85c1e9']
            }
        
        # Chart 3: Column data types distribution
        type_counts = {}
        for col, info in self.analysis_results['column_analysis'].items():
            data_type = info['data_type']
            type_counts[data_type] = type_counts.get(data_type, 0) + 1
        
        charts_data['types_chart'] = {
            'labels': list(type_counts.keys()),
            'data': list(type_counts.values()),
            'title': 'توزيع أنواع البيانات',
            'colors': ['#667eea', '#764ba2', '#f093fb', '#f5576c']
        }
        
        self.analysis_results['charts_data'] = charts_data
    
    def generate_html_dashboard(self, output_path='csv_folder_dashboard.html'):
        """Generate HTML dashboard with local Chart.js"""
        
        if not self.analysis_results:
            print("No analysis results to generate dashboard!")
            return False
        
        charts_data = self.analysis_results.get('charts_data', {})
        
        # Prepare data table (first 100 rows for performance)
        table_data = []
        if self.data is not None:
            sample_data = self.data.head(100)
            for _, row in sample_data.iterrows():
                table_data.append(row.to_dict())
        
        html_content = f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تحليل بيانات مجلد CSV</title>
    <script src="chart.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            direction: rtl;
            line-height: 1.6;
        }}
        
        .navbar {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .navbar .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .navbar h1 {{
            color: white;
            font-size: 1.8rem;
            font-weight: 700;
        }}
        
        .navbar .stats {{
            color: white;
            font-size: 0.9rem;
        }}
        
        .main-container {{
            max-width: 1200px;
            margin: 2rem auto;
            padding: 0 2rem;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}
        
        .card {{
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        }}
        
        .card h3 {{
            color: #667eea;
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .card .number {{
            font-size: 2rem;
            font-weight: bold;
            color: #333;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }}
        
        .chart-title {{
            color: #333;
            margin-bottom: 1rem;
            text-align: center;
            font-size: 1.2rem;
            font-weight: 600;
        }}
        
        .chart-canvas {{
            width: 100% !important;
            max-height: 400px !important;
        }}
        
        .data-table-container {{
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            margin-top: 2rem;
        }}
        
        .table-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        
        .search-box {{
            padding: 0.5rem 1rem;
            border: 2px solid #eee;
            border-radius: 25px;
            font-size: 0.9rem;
            width: 300px;
            transition: border-color 0.3s ease;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        
        .data-table th,
        .data-table td {{
            padding: 0.75rem;
            text-align: right;
            border-bottom: 1px solid #eee;
        }}
        
        .data-table th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #333;
            position: sticky;
            top: 0;
        }}
        
        .data-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .status-indicator {{
            background: #e3f2fd;
            border: 1px solid #2196f3;
            border-radius: 10px;
            padding: 1rem;
            margin-bottom: 1rem;
            font-family: monospace;
            font-size: 0.9rem;
            white-space: pre-wrap;
        }}
        
        @media (max-width: 768px) {{
            .main-container {{
                padding: 0 1rem;
            }}
            
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .search-box {{
                width: 100%;
                margin-bottom: 1rem;
            }}
            
            .table-header {{
                flex-direction: column;
                align-items: stretch;
            }}
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="container">
            <h1><i class="fas fa-chart-bar"></i> تحليل بيانات مجلد CSV</h1>
            <div class="stats">
                <i class="fas fa-database"></i> {self.analysis_results['total_records']} سجل
                <i class="fas fa-file-excel" style="margin-right: 1rem;"></i> {len(self.analysis_results['source_files'])} ملف
            </div>
        </div>
    </nav>

    <div class="main-container">
        <div id="status" class="status-indicator">جاري تحميل البيانات...</div>
        
        <div class="summary-cards">
            <div class="card">
                <h3><i class="fas fa-database"></i> إجمالي السجلات</h3>
                <div class="number">{self.analysis_results['total_records']:,}</div>
            </div>
            <div class="card">
                <h3><i class="fas fa-columns"></i> عدد الأعمدة</h3>
                <div class="number">{self.analysis_results['total_columns']}</div>
            </div>
            <div class="card">
                <h3><i class="fas fa-file-excel"></i> ملفات Excel</h3>
                <div class="number">{len(self.analysis_results['source_files'])}</div>
            </div>
            <div class="card">
                <h3><i class="fas fa-chart-pie"></i> المخططات</h3>
                <div class="number">{len(charts_data)}</div>
            </div>
        </div>

        <div class="charts-grid">'''

        # Add charts
        chart_types = ['bar', 'doughnut', 'pie']
        for i, (chart_key, chart_info) in enumerate(charts_data.items()):
            chart_type = chart_types[i % len(chart_types)]
            html_content += f'''
            <div class="chart-container">
                <div class="chart-title">{chart_info['title']}</div>
                <canvas id="{chart_key}" class="chart-canvas"></canvas>
            </div>'''

        html_content += '''
        </div>

        <div class="data-table-container">
            <div class="table-header">
                <h2><i class="fas fa-table"></i> جدول البيانات (أول 100 سجل)</h2>
                <input type="text" class="search-box" id="searchInput" placeholder="ابحث في البيانات...">
            </div>
            <div style="overflow-x: auto; max-height: 500px;">
                <table class="data-table" id="dataTable">
                    <thead>
                        <tr>'''

        # Add table headers
        if self.data is not None:
            for col in self.data.columns:
                html_content += f'<th>{col}</th>'

        html_content += '''
                        </tr>
                    </thead>
                    <tbody id="tableBody">'''

        # Add table rows
        for row_data in table_data:
            html_content += '<tr>'
            for col in self.data.columns:
                value = row_data.get(col, '')
                if pd.isna(value):
                    value = ''
                html_content += f'<td>{str(value)}</td>'
            html_content += '</tr>'

        html_content += f'''
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const statusDiv = document.getElementById('status');
        
        function updateStatus(message) {{
            const timestamp = new Date().toLocaleTimeString();
            statusDiv.innerHTML += timestamp + ': ' + message + '\\n';
            console.log(message);
        }}
        
        updateStatus('تم تحميل الصفحة');
        updateStatus('Chart.js متاح: ' + (typeof Chart !== 'undefined'));
        
        // Chart data from Python analysis
        const chartsData = {json.dumps(charts_data, ensure_ascii=False, indent=4)};
        
        updateStatus('تم تحميل بيانات المخططات: ' + Object.keys(chartsData).length + ' مخطط');
        
        // Chart configurations
        const chartConfigs = {{
            bar: {{
                responsive: true,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{ 
                        titleFont: {{ size: 14 }},
                        bodyFont: {{ size: 12 }}
                    }}
                }},
                scales: {{
                    y: {{ 
                        beginAtZero: true,
                        ticks: {{ font: {{ size: 11 }} }}
                    }},
                    x: {{ 
                        ticks: {{ 
                            font: {{ size: 10 }},
                            maxRotation: 45
                        }}
                    }}
                }}
            }},
            doughnut: {{
                responsive: true,
                plugins: {{
                    legend: {{ 
                        position: 'bottom',
                        labels: {{ font: {{ size: 11 }} }}
                    }},
                    tooltip: {{ 
                        titleFont: {{ size: 14 }},
                        bodyFont: {{ size: 12 }}
                    }}
                }}
            }},
            pie: {{
                responsive: true,
                plugins: {{
                    legend: {{ 
                        position: 'bottom',
                        labels: {{ font: {{ size: 11 }} }}
                    }},
                    tooltip: {{ 
                        titleFont: {{ size: 14 }},
                        bodyFont: {{ size: 12 }}
                    }}
                }}
            }}
        }};
        
        document.addEventListener('DOMContentLoaded', function() {{
            updateStatus('تم تحميل DOM');
            
            try {{
                if (typeof Chart === 'undefined') {{
                    updateStatus('خطأ: Chart.js غير محمل!');
                    return;
                }}
                
                const chartTypes = ['bar', 'doughnut', 'pie'];
                let chartIndex = 0;
                
                for (const [chartKey, chartData] of Object.entries(chartsData)) {{
                    const canvas = document.getElementById(chartKey);
                    if (!canvas) {{
                        updateStatus('تحذير: لم يتم العثور على canvas للمخطط: ' + chartKey);
                        continue;
                    }}
                    
                    const chartType = chartTypes[chartIndex % chartTypes.length];
                    chartIndex++;
                    
                    const ctx = canvas.getContext('2d');
                    
                    new Chart(ctx, {{
                        type: chartType,
                        data: {{
                            labels: chartData.labels,
                            datasets: [{{
                                label: chartData.title,
                                data: chartData.data,
                                backgroundColor: chartData.colors.slice(0, chartData.data.length),
                                borderWidth: 2,
                                borderRadius: chartType === 'bar' ? 5 : 0
                            }}]
                        }},
                        options: chartConfigs[chartType]
                    }});
                    
                    updateStatus('تم إنشاء مخطط: ' + chartKey + ' (' + chartType + ')');
                }}
                
                updateStatus('✅ تم إنشاء جميع المخططات بنجاح!');
                
            }} catch (error) {{
                updateStatus('❌ خطأ: ' + error.message);
                updateStatus('Stack: ' + error.stack);
            }}
            
            // Search functionality
            const searchInput = document.getElementById('searchInput');
            const tableBody = document.getElementById('tableBody');
            const originalRows = Array.from(tableBody.getElementsByTagName('tr'));
            
            searchInput.addEventListener('input', function() {{
                const searchTerm = this.value.toLowerCase();
                
                originalRows.forEach(row => {{
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {{
                        row.style.display = '';
                    }} else {{
                        row.style.display = 'none';
                    }}
                }});
            }});
            
            updateStatus('تم تفعيل وظيفة البحث');
        }});
        
        // Catch any global errors
        window.onerror = function(msg, url, line, col, error) {{
            updateStatus('❌ خطأ عام: ' + msg + ' في السطر ' + line);
            return false;
        }};
        
        updateStatus('تم الانتهاء من الإعداد');
    </script>
</body>
</html>'''

        # Write the HTML file
        output_file = Path(output_path)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\\n✅ Dashboard generated: {output_file.absolute()}")
        print(f"📊 Charts created: {len(charts_data)}")
        print(f"📋 Data table rows: {len(table_data)}")
        
        return True

def main():
    """Main execution function"""
    print("🚀 تحليل بيانات مجلد CSV")
    print("=" * 50)
    
    # Initialize analyzer
    csv_folder = "/Users/ahmedgomaa/Documents/pytextai/csvs"
    analyzer = CSVFolderAnalyzer(csv_folder)
    
    # Load and analyze data
    if analyzer.load_excel_files():
        if analyzer.analyze_data():
            # Generate dashboard
            analyzer.generate_html_dashboard('csv_folder_dashboard.html')
            
            print("\\n🎉 تم إنشاء لوحة التحكم بنجاح!")
            print("📂 افتح الملف: csv_folder_dashboard.html")
            print("🌐 أو استخدم: http://localhost:8080/csv_folder_dashboard.html")
        else:
            print("❌ فشل في تحليل البيانات")
    else:
        print("❌ فشل في تحميل البيانات")

if __name__ == "__main__":
    main()
