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

# Enable CORS for all routes
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Database connection
DB_PATH = 'real_estate_data.db'

def check_database():
    """Check if database file exists and is accessible."""
    if not os.path.exists(DB_PATH):
        return False, f"Database file '{DB_PATH}' not found"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        
        if not tables:
            return False, "Database exists but contains no tables"
        
        return True, f"Database connected successfully with {len(tables)} tables"
    except Exception as e:
        return False, f"Database connection error: {str(e)}"

def get_db_connection():
    """Get database connection."""
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database file '{DB_PATH}' not found")
    
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
        print(f"Database query error: {str(e)}")
        return {'error': str(e)}

# API Routes

@app.route('/health')
def health():
    """Health check endpoint."""
    db_ok, db_message = check_database()
    return jsonify({
        'status': 'healthy' if db_ok else 'unhealthy',
        'database': db_message,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/frontend')
def frontend():
    """Serve the API frontend HTML page."""
    try:
        # Check if database is accessible first
        db_ok, db_message = check_database()
        if not db_ok:
            return f"""
            <html>
            <head><title>Database Error</title></head>
            <body>
                <h1>Database Connection Error</h1>
                <p>Error: {db_message}</p>
                <p>Please check your database file and try again.</p>
            </body>
            </html>
            """, 500
        
        with open('api_frontend.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return jsonify({
            'error': 'Frontend HTML file not found',
            'message': 'Make sure api_frontend.html is in the same directory as this script'
        }), 404
    except Exception as e:
        return jsonify({
            'error': 'Error loading frontend',
            'message': str(e)
        }), 500

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
                <code>/api/properties</code> - Get all properties with pagination and filtering
                <br><small>Parameters: page, limit, region, property_type, sender, search</small>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <code>/property/{unique_id}</code> - Get specific property details
                <br><small>Example: /property/123456</small>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span>
                <code>/api/property</code> - Add new property
                <br><small>Body: JSON with property data</small>
            </div>
            
            <div class="endpoint">
                <span class="method">PUT</span>
                <code>/property/{unique_id}</code> - Update existing property
                <br><small>Body: JSON with updated property data</small>
            </div>
            
            <div class="endpoint">
                <span class="method">DELETE</span>
                <code>/property/{unique_id}</code> - Delete property
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span>
                <code>/api/remove-duplicates</code> - Remove duplicate properties based on message
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span>
                <code>/api/search</code> - Search properties
                <br><small>Parameters: q (query), limit (default: 50)</small>
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
            // Load stats on page load
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    const statsDiv = document.getElementById('stats');
                    statsDiv.innerHTML = `
                        <div class="stat-card">
                            <div class="stat-number">${data.total_properties}</div>
                            <div class="stat-label">Total Properties</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.unique_senders}</div>
                            <div class="stat-label">Unique Senders</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.unique_regions}</div>
                            <div class="stat-label">Regions</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-number">${data.unique_property_types}</div>
                            <div class="stat-label">Property Types</div>
                        </div>
                    `;
                })
                .catch(error => {
                    console.error('Error loading stats:', error);
                    document.getElementById('stats').innerHTML = '<p>Error loading statistics</p>';
                });
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
    """Get properties with pagination and filtering."""
    page = int(request.args.get('page', 1))
    limit = min(int(request.args.get('limit', 50)), 1000)  # Max 1000 per page
    offset = (page - 1) * limit
    
    # Get filter parameters
    region_filter = request.args.get('region', '')
    property_type_filter = request.args.get('property_type', '')
    sender_filter = request.args.get('sender', '')
    search_query = request.args.get('search', '')
    
    # Build WHERE clause
    where_conditions = []
    params = []
    
    if region_filter:
        where_conditions.append("region LIKE ?")
        params.append(f"%{region_filter}%")
    
    if property_type_filter:
        where_conditions.append("property_type LIKE ?")
        params.append(f"%{property_type_filter}%")
    
    if sender_filter:
        where_conditions.append("sender_name LIKE ?")
        params.append(f"%{sender_filter}%")
    
    if search_query:
        # Enhanced smart search logic
        cleaned_search = search_query.strip().lower()
        search_words = [word.strip() for word in cleaned_search.split() if word.strip()]
        
        search_parts = []
        for word in search_words:
            # Create multiple patterns for enhanced fuzzy matching
            patterns = [
                f"%{word}%",  # Exact match
                f"%{word.replace(' ', '')}%",  # No spaces
            ]
            
            # Add number variations
            if any(c.isdigit() for c in word):
                number_clean = ''.join(c for c in word if c.isdigit())
                if number_clean:
                    patterns.extend([f"%{number_clean}%", f"%0{number_clean}%"])
            
            # Enhanced character variations for better typo tolerance
            if len(word) >= 3:
                # Missing character variations
                for i in range(len(word)):
                    variant = word[:i] + word[i+1:]
                    if len(variant) >= 2:
                        patterns.append(f"%{variant}%")
                
                # Remove characters from ends
                patterns.extend([
                    f"%{word[:-1]}%",  # Missing last char
                    f"%{word[1:]}%",   # Missing first char
                ])
                
                # Partial matching for longer words
                if len(word) >= 4:
                    patterns.extend([
                        f"{word[:3]}%",    # Starts with first 3 chars
                        f"%{word[-3:]}",   # Ends with last 3 chars
                    ])
            
            # Create OR condition for this word
            word_conditions = []
            for pattern in patterns:
                word_conditions.append("(message LIKE ? OR region LIKE ? OR property_type LIKE ? OR sender_name LIKE ? OR sender_phone LIKE ? OR sender_phone_2 LIKE ?)")
                params.extend([pattern] * 6)
            
            search_parts.append("(" + " OR ".join(word_conditions) + ")")
        
        # All words must match (AND)
        if search_parts:
            where_conditions.append("(" + " AND ".join(search_parts) + ")")
    
    
    where_clause = ""
    if where_conditions:
        where_clause = "WHERE " + " AND ".join(where_conditions)
    
    query = f"""
    SELECT unique_id, sender_name, sender_phone, sender_phone_2, region, property_type, message, date, time
    FROM properties 
    {where_clause}
    ORDER BY date DESC, time DESC
    LIMIT ? OFFSET ?
    """
    
    params.extend([limit, offset])
    properties = execute_query(query, params)
    
    # Get total count with filters
    count_query = f"SELECT COUNT(*) as total FROM properties {where_clause}"
    count_params = params[:-2]  # Remove limit and offset
    total_result = execute_query(count_query, count_params)
    total = total_result[0]['total'] if total_result and not isinstance(total_result, dict) else 0
    
    return jsonify({
        'data': properties,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'has_more': offset + len(properties) < total if properties and not isinstance(properties, dict) else False
        }
    })

@app.route('/api/search')
def search_properties():
    """Enhanced smart search properties by query with precise Arabic number matching."""
    query = request.args.get('q', '')
    limit = min(int(request.args.get('limit', 50)), 1000)
    
    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400
    
    # Clean and prepare search query
    cleaned_query = query.strip()
    
    # Split query into individual words for better matching
    search_words = [word.strip() for word in cleaned_query.split() if word.strip()]
    
    # Build enhanced search conditions
    search_conditions = []
    search_params = []
    
    for word in search_words:
        word_patterns = []
        
        # Check if this word contains Arabic numbers or district/neighborhood terms
        has_arabic_numbers = any(c in '٠١٢٣٤٥٦٧٨٩' for c in word)
        has_english_numbers = any(c.isdigit() for c in word)
        is_district_term = any(term in word.lower() for term in ['الحي', 'حي', 'مجاورة', 'مجاوره', 'مج'])
        
        if has_arabic_numbers or (has_english_numbers and is_district_term):
            # For district/neighborhood searches with numbers, be more precise
            # 1. Exact match with highest priority
            word_patterns.append(f"%{word}%")
            
            # 2. Handle Arabic/English number variations
            if has_arabic_numbers:
                # Convert Arabic numbers to English
                arabic_to_english = {'٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4', 
                                   '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9'}
                english_version = word
                for ar, en in arabic_to_english.items():
                    english_version = english_version.replace(ar, en)
                word_patterns.append(f"%{english_version}%")
            
            if has_english_numbers:
                # Convert English numbers to Arabic
                english_to_arabic = {'0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤', 
                                   '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'}
                arabic_version = word
                for en, ar in english_to_arabic.items():
                    arabic_version = arabic_version.replace(en, ar)
                word_patterns.append(f"%{arabic_version}%")
            
            # 3. Handle spacing variations only for district terms
            if is_district_term:
                word_no_space = word.replace(' ', '')
                word_patterns.append(f"%{word_no_space}%")
                word_with_space = word.replace('الحي', 'الحي ').replace('حي', 'حي ').replace('مجاورة', 'مجاورة ').replace('مجاوره', 'مجاوره ')
                word_patterns.append(f"%{word_with_space}%")
            
            # 4. Handle abbreviated forms
            if 'مجاورة' in word or 'مجاوره' in word:
                # Add "مج" abbreviation
                abbreviated = word.replace('مجاورة', 'مج').replace('مجاوره', 'مج')
                word_patterns.append(f"%{abbreviated}%")
            elif 'مج' in word:
                # Expand "مج" to full forms
                full_forms = [word.replace('مج', 'مجاورة'), word.replace('مج', 'مجاوره')]
                for form in full_forms:
                    word_patterns.append(f"%{form}%")
        
        else:
            # For non-district terms, use regular fuzzy matching
            word_lower = word.lower()
            
            # 1. Exact match (highest priority)
            word_patterns.append(f"%{word}%")
            word_patterns.append(f"%{word_lower}%")
            
            # 2. Case variations
            word_patterns.append(f"%{word.upper()}%")
            word_patterns.append(f"%{word.title()}%")
            
            # 3. Only add fuzzy matching for longer words (4+ characters)
            if len(word) >= 4:
                # Missing character tolerance (only 1 character)
                for i in range(len(word)):
                    variant = word[:i] + word[i+1:]
                    if len(variant) >= 3:
                        word_patterns.append(f"%{variant}%")
                
                # Character substitution for common Arabic typos
                if any(c in 'أإآءةهى' for c in word):
                    common_substitutions = {
                        'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ء': '',
                        'ة': 'ه', 'ه': 'ة', 'ى': 'ي', 'ي': 'ى'
                    }
                    for old_char, new_char in common_substitutions.items():
                        if old_char in word:
                            substituted = word.replace(old_char, new_char)
                            word_patterns.append(f"%{substituted}%")
            
            # 4. Handle regular numbers
            if has_english_numbers:
                # Search in phone numbers and area sizes
                number_clean = ''.join(c for c in word if c.isdigit())
                if number_clean and len(number_clean) >= 2:
                    word_patterns.append(f"%{number_clean}%")
        
        # Create OR condition for this word across relevant fields
        word_condition = " OR ".join([
            "(message LIKE ? OR sender_name LIKE ? OR region LIKE ? OR property_type LIKE ? OR sender_phone LIKE ? OR sender_phone_2 LIKE ?)"
            for _ in word_patterns
        ])
        
        search_conditions.append(f"({word_condition})")
        
        # Add parameters for each pattern across all fields
        for pattern in word_patterns:
            search_params.extend([pattern] * 6)  # 6 fields per pattern
    
    # Combine all word conditions with AND (all words must match somewhere)
    final_condition = " AND ".join(search_conditions)
    
    sql = f"""
    SELECT unique_id, sender_name, sender_phone, sender_phone_2, region, property_type, message, date, time,
           CASE 
               WHEN message LIKE ? OR region LIKE ? THEN 10
               WHEN sender_name LIKE ? THEN 8
               WHEN property_type LIKE ? THEN 6
               WHEN sender_phone LIKE ? OR sender_phone_2 LIKE ? THEN 7
               ELSE 1
           END as relevance_score
    FROM properties 
    WHERE {final_condition}
    ORDER BY relevance_score DESC, date DESC, time DESC
    LIMIT ?
    """
    
    # Add relevance scoring parameters (prioritize exact matches)
    exact_query = f"%{cleaned_query}%"
    relevance_params = [exact_query, exact_query, exact_query, exact_query, exact_query, exact_query]
    
    # Combine all parameters
    all_params = relevance_params + search_params + [limit]
    
    properties = execute_query(sql, all_params)
    
    return jsonify({
        'data': properties,
        'count': len(properties) if properties and not isinstance(properties, dict) else 0,
        'query': query,
        'search_words': search_words
    })

@app.route('/api/regions')
def get_regions():
    """Get all regions with property counts."""
    query = """
    SELECT region, COUNT(*) as count
    FROM properties 
    WHERE region != ''
    GROUP BY region 
    ORDER BY count DESC
    LIMIT ?
    """
    
    limit = min(int(request.args.get('limit', 100)), 1000)
    regions = execute_query(query, (limit,))
    
    return jsonify({
        'status': 'success',
        'data': regions
    })

@app.route('/api/regions/<region_name>/properties')
def get_properties_by_region(region_name):
    """Get properties for a specific region."""
    limit = min(int(request.args.get('limit', 50)), 1000)
    
    query = """
    SELECT unique_id, sender_name, sender_phone, sender_phone_2, property_type, message, date, time
    FROM properties 
    WHERE region LIKE ?
    ORDER BY date DESC, time DESC
    LIMIT ?
    """
    
    properties = execute_query(query, (f"%{region_name}%", limit))
    
    return jsonify({
        'status': 'success',
        'region': region_name,
        'data': properties,
        'count': len(properties) if properties and not isinstance(properties, dict) else 0
    })

@app.route('/api/senders')
def get_senders():
    """Get top senders by number of properties."""
    limit = min(int(request.args.get('limit', 50)), 1000)
    
    query = """
    SELECT sender_name, COUNT(*) as count
    FROM properties 
    WHERE sender_name != ''
    GROUP BY sender_name 
    ORDER BY count DESC
    LIMIT ?
    """
    
    senders = execute_query(query, (limit,))
    
    return jsonify({
        'status': 'success',
        'data': senders
    })

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

@app.route('/property/<unique_id>')
def get_property_by_id(unique_id):
    """Get a specific property by its unique ID."""
    try:
        query = """
        SELECT unique_id, sender_name, sender_phone, sender_phone_2, region, property_type, message, date, time
        FROM properties 
        WHERE unique_id = ?
        """
        
        result = execute_query(query, (unique_id,))
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({'status': 'error', 'message': result['error']}), 500
        
        if not result:
            return jsonify({'status': 'error', 'message': 'Property not found'}), 404
        
        return jsonify({
            'status': 'success',
            'data': result[0]
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# CRUD Operations

@app.route('/api/property', methods=['POST'])
def add_property():
    """Add a new property."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Generate unique_id if not provided
        if 'unique_id' not in data or not data['unique_id']:
            import time
            data['unique_id'] = f"PROP_{int(time.time())}"
        
        query = """
        INSERT INTO properties (unique_id, sender_name, region, property_type, message, date, time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (
            data.get('unique_id'),
            data.get('sender_name', ''),
            data.get('region', ''),
            data.get('property_type', ''),
            data.get('message', ''),
            data.get('date', ''),
            data.get('time', '')
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Property added successfully', 'unique_id': data['unique_id']})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/property/<unique_id>', methods=['PUT'])
def update_property(unique_id):
    """Update an existing property."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        query = """
        UPDATE properties 
        SET sender_name = ?, region = ?, property_type = ?, message = ?, date = ?, time = ?
        WHERE unique_id = ?
        """
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (
            data.get('sender_name', ''),
            data.get('region', ''),
            data.get('property_type', ''),
            data.get('message', ''),
            data.get('date', ''),
            data.get('time', ''),
            unique_id
        ))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Property not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Property updated successfully'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/property/<unique_id>', methods=['DELETE'])
def delete_property(unique_id):
    """Delete a property."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM properties WHERE unique_id = ?", (unique_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Property not found'}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Property deleted successfully'})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/remove-duplicates', methods=['POST'])
def remove_duplicates():
    """Remove duplicate properties based on message content."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find duplicates based on message
        find_duplicates_query = """
        SELECT message, COUNT(*) as count, GROUP_CONCAT(unique_id) as ids
        FROM properties 
        WHERE message != '' 
        GROUP BY message 
        HAVING COUNT(*) > 1
        """
        
        cursor.execute(find_duplicates_query)
        duplicates = cursor.fetchall()
        
        total_removed = 0
        for row in duplicates:
            ids = row[2].split(',')  # Get all IDs for this message
            # Keep the first one, delete the rest
            ids_to_delete = ids[1:]
            for id_to_delete in ids_to_delete:
                cursor.execute("DELETE FROM properties WHERE unique_id = ?", (id_to_delete,))
                total_removed += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success', 
            'message': f'Removed {total_removed} duplicate properties',
            'duplicates_found': len(duplicates),
            'total_removed': total_removed
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

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
        
        if isinstance(result, dict) and 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'sql': sql,
            'count': len(result) if result else 0,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🏠 Real Estate Database API Server")
    print("=" * 40)
    print(f"Database: {DB_PATH}")
    
    # Check database before starting server
    db_ok, db_message = check_database()
    if db_ok:
        print(f"✅ {db_message}")
    else:
        print(f"❌ {db_message}")
        print("⚠️  Server will start but database operations may fail")
    
    print("API Documentation: http://localhost:8000")
    print("Frontend: http://localhost:8000/frontend")
    print("Health Check: http://localhost:8000/health")
    print("=" * 40)
    
    app.run(host='0.0.0.0', port=8000, debug=True)
