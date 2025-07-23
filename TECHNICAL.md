# TECHNICAL DOCUMENTATION 🛠️

## Project Overview
**WhatsApp Chat Parser & Data Extraction System**

This project is a comprehensive Python-based system designed to parse, clean, and extract structured data from exported WhatsApp group chat .txt files. The system processes raw chat exports and converts them into clean, structured CSV data suitable for analysis and business intelligence.

## 🏗️ Architecture & Design

### Core Components

#### 1. Main Parser (`simple_parser.py`)
- **Primary script** that handles the complete parsing workflow
- Processes all WhatsApp chat files in the `whatsapp_chat_exports/` directory
- Outputs structured data to `whatsapp_chats.csv`

#### 2. Data Processing Pipeline
```
Raw .txt files → Unicode Cleaning → Message Parsing → Data Extraction → CSV Export
```

### 🔄 Processing Workflow

#### Phase 1: File Discovery & Setup
- Scans `whatsapp_chat_exports/` directory for `_chat*.txt` files
- Initializes data structures for message storage

#### Phase 2: Text Processing & Cleaning
- **Unicode Normalization**: Removes directional marks, non-breaking spaces
- **Line Parsing**: Extracts timestamp, sender, and message content
- **Multi-line Message Handling**: Concatenates continuation lines

#### Phase 3: Data Extraction
- **Phone Number Extraction**: Multiple regex patterns for various formats
- **Emoji Removal**: Comprehensive Unicode emoji pattern matching
- **Media Reference Cleaning**: Removes "image omitted", "video omitted" patterns
- **Status Keyword Extraction**: Identifies property-related terms (Arabic/English)

#### Phase 4: Data Structuring
- **Unique ID Generation**: Sequential PRO1, PRO2, ... format
- **Dual Phone Support**: Primary and secondary phone number fields
- **Message Backup**: Preserves original message before cleaning
- **Status Classification**: Property sale/rent/wanted keywords

#### Phase 5: CSV Export
- Structured output with 11 columns
- UTF-8 encoding for multilingual support
- Statistical summary generation

## 📊 Data Schema

### CSV Output Structure
| Column | Type | Description |
|--------|------|-------------|
| `unique_id` | String | Sequential identifier (PRO1, PRO2, ...) |
| `file_source` | String | Source .txt filename |
| `date` | String | Message date (DD/MM/YYYY) |
| `time` | String | Message time (HH:MM:SS AM/PM) |
| `sender_name` | String | Cleaned sender name (emojis removed) |
| `sender_phone` | String | Primary phone number |
| `sender_phone_2` | String | Secondary phone number extracted from message |
| `message` | String | Cleaned message content |
| `message_backup` | String | Original message before cleaning |
| `status` | String | Property-related keywords found |
| `line_number` | Integer | Line number in source file |

## 🔍 Regex Patterns & Algorithms

### Message Parsing Pattern
```regex
^\[(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}:\d{2} (?:AM|PM))\] ([^:]+): (.*)$
```

### Phone Number Extraction Patterns
1. **Egyptian Mobile**: `(01[0125]\d{8})`
2. **International Format**: `\+20\s*(\d{3})\s*(\d{3})\s*(\d{4})`
3. **Arabic-Indic Digits**: `([٠-٩]{10,11})`
4. **Flexible Spacing**: `(01[0125][\s\-\.\u00A0]*\d[\s\-\.\u00A0]*...)`

### Emoji Removal Pattern
- Covers Unicode ranges: U+1F600-U+1F64F, U+1F300-U+1F5FF, etc.
- Handles directional marks and special characters

### Media Reference Patterns
- Timestamped media: `\[\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} (?:AM|PM)\] [^:]*: (?:image|video) omitted`
- Deleted messages: `This message was deleted`
- WhatsApp notifications: `This message can't be displayed here...`

## 🏷️ Status Keyword Classification

### Arabic Keywords
- Sale: `للبيع`, `بيع`
- Wanted: `مطلوب`
- Offered: `معروض`
- Rent: `ايجار`, `للايجار`, `للإيجار`
- Investment: `للاستثمار`, `استثمار`

### English Keywords
- Sale: `for sale`, `sale`, `selling`, `sell`
- Wanted: `wanted`, `required`, `looking for`
- Offered: `offered`, `available`, `offering`
- Rent: `rent`, `rental`, `for rent`, `renting`
- Investment: `investment`, `lease`, `leasing`

## 🗂️ File Organization

### Directory Structure
```
pytextai/
├── simple_parser.py           # Main processing script
├── whatsapp_chat_exports/     # Raw .txt chat files
│   ├── _chat.txt
│   ├── _chat 2.txt
│   └── ... (14 files total)
├── whatsapp_chats.csv         # Processed output
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation
└── TECHNICAL.md              # This technical guide
```

## ⚡ Performance Characteristics

### Processing Metrics (Last Run)
- **Total Messages**: 57,488
- **Processing Time**: ~30-60 seconds
- **Memory Usage**: Moderate (all messages loaded in memory)
- **Phone Numbers Extracted**: 45,077 (78.4%)
- **Status Keywords Found**: 47,496 (82.6%)
- **Unique Senders**: 478

### Scalability Considerations
- **Memory**: Linear growth with message count
- **Processing**: O(n) time complexity
- **Storage**: CSV output scales linearly
- **Regex Performance**: Optimized patterns for speed

## 🔧 Dependencies & Requirements

### Python Version
- **Minimum**: Python 3.6+
- **Recommended**: Python 3.8+

### Standard Library Modules
- `re` - Regular expression operations
- `csv` - CSV file handling
- `glob` - File pattern matching
- `os` - Operating system interface

### External Dependencies
- None (uses only Python standard library)

## 🚀 Deployment & Usage

### Command Line Execution
```bash
cd /path/to/pytextai
python3 simple_parser.py
```

### Expected Output
```
🔍 WhatsApp Chat Parser - Simple Version
==================================================
Found 14 chat files
Processing: whatsapp_chat_exports/_chat.txt
  - Extracted 2648 messages
...
✅ CSV saved: whatsapp_chats.csv
📊 Statistics:
  - Total messages: 57488
  - Messages with phone numbers: 45077
  - Messages with second phone numbers: 5343
  - Messages with status keywords: 47496
  - Unique senders: 478
```

## 🔄 Maintenance & Updates

### Adding New Keywords
Update the `extract_status_keywords()` function:
```python
arabic_keywords = [
    # Add new Arabic terms
]
english_keywords = [
    # Add new English terms
]
```

### Phone Number Patterns
Add new patterns to `additional_patterns` list in main processing loop.

### Output Format Changes
Modify `headers` list and message dictionary structure.

## 🐛 Common Issues & Solutions

### Unicode Handling
- **Issue**: Garbled Arabic text
- **Solution**: Ensure UTF-8 encoding in file operations

### Memory Usage
- **Issue**: Large files causing memory issues
- **Solution**: Process files in chunks (future enhancement)

### Regex Performance
- **Issue**: Slow processing on large messages
- **Solution**: Optimize regex patterns, consider compilation

## 🔮 Future Enhancements

### Phase 1: Performance
- Streaming file processing
- Regex pattern compilation
- Parallel file processing

### Phase 2: Features
- Date range filtering
- Sender analytics
- Export format options (JSON, Excel)

### Phase 3: Intelligence
- ML-based classification
- Sentiment analysis
- Named entity recognition

## 🔐 Security Considerations

### Data Privacy
- No external API calls
- Local processing only
- No data transmission

### File Handling
- Input validation
- Error handling for corrupted files
- Safe file operations

## 📈 Analytics & Insights

### Key Metrics Tracked
- Message volume per file
- Phone number extraction rate
- Status keyword frequency
- Sender activity patterns

### Business Intelligence Potential
- Property market trend analysis
- Customer engagement metrics
- Lead generation analytics
- Sentiment tracking

---

## 🤖 AI Agent Collaboration Notes

### For Future AI Agents Working on This Project:

1. **Core Logic**: The main processing happens in `simple_parser.py` - this is your primary focus
2. **Data Flow**: Raw .txt → Unicode cleaning → Parsing → Extraction → CSV
3. **Critical Functions**: 
   - `parse_message()` - Core message parsing
   - `extract_status_keywords()` - Business logic for classification
   - `remove_emojis()` - Text cleaning
4. **File Organization**: All raw data is in `whatsapp_chat_exports/`
5. **Output**: Always maintain the CSV schema for consistency
6. **Testing**: Use the provided sample data for validation
7. **Performance**: Consider memory usage when processing large datasets

### Extension Points:
- Add new regex patterns for phone extraction
- Extend status keywords for new business domains
- Implement additional cleaning rules
- Add new output formats
- Integrate with databases or APIs

### Code Quality:
- Maintain UTF-8 encoding throughout
- Document regex patterns clearly
- Use descriptive variable names
- Add error handling for edge cases
- Keep processing statistics for monitoring

---

*Last Updated: July 2025*
*Version: 1.0.0*
*Maintainer: AI Development Team*
