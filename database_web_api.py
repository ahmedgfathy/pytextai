#!/usr/bin/env python3
"""
Web API Server for Real Estate SQLite Database
Simple Flask-based API to serve real estate data from SQLite database.

Author: Real Estate Data Processing System
Date: 2025
"""

from flask import Flask, jsonify, request, render_template_string, send_from_directory
import sqlite3
import json
import os
from datetime import datetime

app = Flask(__name__)

# Database connection
DB_PATH = 'real_estate_data.db'

def get_db_connection():
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def execute_query(query, params=None):
    """Execute a query and return results as list of dictionaries."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        
        conn.close()
        return result
    except Exception as e:
        return {'error': str(e)}

# API Routes

@app.route('/frontend')
def frontend():
    """Serve the API frontend HTML page."""
    try:
        with open('api_frontend.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({
            'error': 'Frontend HTML file not found',
            'message': 'Make sure api_frontend.html is in the same directory as this script'
        }), 404

@app.route('/')
def index():
    """Main page with API documentation."""
    html = """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Real Estate API</title>
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 40px; 
                background-color: #f5f5f5; 
                color: #333;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                background: white; 
                padding: 30px; 
                border-radius: 10px; 
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #2c5aa0; margin-bottom: 30px; }
            h2 { color: #34495e; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }
            .endpoint { 
                background: #ecf0f1; 
                padding: 15px; 
                margin: 10px 0; 
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }
            .method { 
                background: #3498db; 
                color: white; 
                padding: 5px 10px; 
                border-radius: 3px; 
                font-weight: bold;
                display: inline-block;
                margin-right: 10px;
            }
            code { 
                background: #2c3e50; 
                color: #ecf0f1; 
                padding: 2px 6px; 
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
            .stats { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 20px; 
                margin: 30px 0;
            }
            .stat-card { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                padding: 20px; 
                border-radius: 10px; 
                text-align: center;
            }
            .stat-number { font-size: 2em; font-weight: bold; }
            .stat-label { font-size: 0.9em; opacity: 0.9; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏠 Real Estate Database API</h1>
            
            <div class="stats" id="stats">
                <!-- Stats will be loaded here -->
            </div>
            
            <h2>📡 API Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <code>/api/stats</code> - Get database statistics
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <code>/api/properties</code> - Get all properties (paginated)
                <br><small>Parameters: page (default: 1), limit (default: 50, max: 1000)</small>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <code>/api/search?q=keyword</code> - Search properties by keyword
                <br><small>Parameters: q (required), limit (default: 50)</small>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <code>/api/regions</code> - Get all regions with counts
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <code>/api/regions/{region}/properties</code> - Get properties by region
                <br><small>Parameters: limit (default: 50)</small>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <code>/api/senders</code> - Get top senders
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <code>/api/property-types</code> - Get property types with counts
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span>
                <code>/api/query</code> - Execute custom SQL query
                <br><small>Body: {"sql": "SELECT * FROM properties LIMIT 10"}</small>
            </div>
            
            <h2>📋 Examples</h2>
            <ul>
                <li><a href="/api/stats">/api/stats</a></li>
                <li><a href="/api/properties?limit=10">/api/properties?limit=10</a></li>
                <li><a href="/api/search?q=شقة&limit=5">/api/search?q=شقة&limit=5</a></li>
                <li><a href="/api/regions">/api/regions</a></li>
                <li><a href="/api/property-types">/api/property-types</a></li>
            </ul>
        </div>
        
        <script>
            // Load stats
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    const statsDiv = document.getElementById('stats');
                    statsDiv.innerHTML = `
                        <div class="stat-card">
                            <div class="stat-number">${data.total_properties.toLocaleString()}</div>
                            <div class="stat-label">Total Properties</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.unique_senders.toLocaleString()}</div>
                            <div class="stat-label">Unique Senders</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.unique_regions.toLocaleString()}</div>
                            <div class="stat-label">Unique Regions</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.unique_property_types}</div>
                            <div class="stat-label">Property Types</div>
                        </div>
                    `;
                })
                .catch(error => console.error('Error loading stats:', error));
        </script>
    </body>
    </html>
    """
    return html

@app.route('/api/stats')
def get_stats():
    """Get database statistics."""
    stats = {}
    
    # Total properties
    result = execute_query("SELECT COUNT(*) as total FROM properties")
    stats['total_properties'] = result[0]['total'] if result and not isinstance(result, dict) else 0
    
    # Unique senders
    result = execute_query("SELECT COUNT(DISTINCT sender_name) as count FROM properties WHERE sender_name != ''")
    stats['unique_senders'] = result[0]['count'] if result and not isinstance(result, dict) else 0
    
    # Unique regions
    result = execute_query("SELECT COUNT(DISTINCT region) as count FROM properties WHERE region != ''")
    stats['unique_regions'] = result[0]['count'] if result and not isinstance(result, dict) else 0
    
    # Unique property types
    result = execute_query("SELECT COUNT(DISTINCT property_type) as count FROM properties WHERE property_type != ''")
    stats['unique_property_types'] = result[0]['count'] if result and not isinstance(result, dict) else 0
    
    return jsonify(stats)

@app.route('/api/properties')
def get_properties():
    """Get properties with pagination."""
    page = int(request.args.get('page', 1))
    limit = min(int(request.args.get('limit', 50)), 1000)  # Max 1000 per page
    offset = (page - 1) * limit
    
    query = """
    SELECT unique_id, sender_name, region, property_type, message, date, time
    FROM properties 
    ORDER BY date DESC, time DESC
    LIMIT ? OFFSET ?
    """
    
    properties = execute_query(query, (limit, offset))
    
    # Get total count
    total_result = execute_query("SELECT COUNT(*) as total FROM properties")
    total = total_result[0]['total'] if total_result and not isinstance(total_result, dict) else 0
    
    return jsonify({
        'properties': properties,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    })

@app.route('/api/search')
def search_properties():
    """Search properties by keyword."""
    keyword = request.args.get('q', '')
    limit = min(int(request.args.get('limit', 50)), 1000)
    
    if not keyword:
        return jsonify({'error': 'Missing search keyword (q parameter)'}), 400
    
    query = """
    SELECT unique_id, sender_name, region, property_type, message, date, time
    FROM properties 
    WHERE message LIKE ? OR region LIKE ? OR property_type LIKE ? OR sender_name LIKE ?
    ORDER BY date DESC, time DESC
    LIMIT ?
    """
    
    keyword_pattern = f"%{keyword}%"
    properties = execute_query(query, (keyword_pattern, keyword_pattern, keyword_pattern, keyword_pattern, limit))
    
    return jsonify({
        'keyword': keyword,
        'count': len(properties) if not isinstance(properties, dict) else 0,
        'properties': properties
    })

@app.route('/api/regions')
def get_regions():
    """Get all regions with counts."""
    query = """
    SELECT region, COUNT(*) as count
    FROM properties 
    WHERE region != ''
    GROUP BY region 
    ORDER BY count DESC
    """
    
    regions = execute_query(query)
    return jsonify(regions)

@app.route('/api/regions/<region_name>/properties')
def get_properties_by_region(region_name):
    """Get properties from a specific region."""
    limit = min(int(request.args.get('limit', 50)), 1000)
    
    query = """
    SELECT unique_id, sender_name, property_type, message, date, time
    FROM properties 
    WHERE region LIKE ?
    ORDER BY date DESC, time DESC
    LIMIT ?
    """
    
    properties = execute_query(query, (f"%{region_name}%", limit))
    
    return jsonify({
        'region': region_name,
        'count': len(properties) if not isinstance(properties, dict) else 0,
        'properties': properties
    })

@app.route('/api/senders')
def get_senders():
    """Get top senders."""
    limit = min(int(request.args.get('limit', 50)), 1000)
    
    query = """
    SELECT sender_name, COUNT(*) as messages_count
    FROM properties 
    WHERE sender_name != ''
    GROUP BY sender_name 
    ORDER BY messages_count DESC
    LIMIT ?
    """
    
    senders = execute_query(query, (limit,))
    return jsonify(senders)

@app.route('/api/property-types')
def get_property_types():
    """Get property types with counts."""
    query = """
    SELECT property_type, COUNT(*) as count
    FROM properties 
    WHERE property_type != ''
    GROUP BY property_type 
    ORDER BY count DESC
    """
    
    types = execute_query(query)
    return jsonify(types)

@app.route('/api/query', methods=['POST'])
def custom_query():
    """Execute custom SQL query."""
    try:
        data = request.get_json()
        if not data or 'sql' not in data:
            return jsonify({'error': 'Missing SQL query in request body'}), 400
        
        sql = data['sql'].strip()
        
        # Basic security: only allow SELECT statements
        if not sql.upper().startswith('SELECT'):
            return jsonify({'error': 'Only SELECT queries are allowed'}), 400
        
        # Limit results to prevent abuse
        if 'LIMIT' not in sql.upper():
            sql += ' LIMIT 1000'
        
        result = execute_query(sql)
        
        return jsonify({
            'sql': sql,
            'count': len(result) if not isinstance(result, dict) else 0,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🏠 Real Estate Database API Server")
    print("=" * 40)
    print(f"Database: {DB_PATH}")
    print("API Documentation: http://localhost:5000")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
