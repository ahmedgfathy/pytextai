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
**Unicode Normalization**: Removes directional marks, non-breaking spaces
**Line Parsing**: Extracts timestamp, sender, and message content
**Multi-line Message Handling**: Concatenates continuation lines
**Word Frequency Analysis**: Extracts and counts both English and Arabic words from WhatsApp chats, ignoring numbers, emojis, and punctuation. Results are sorted by frequency and written to a text file. Example top results:
```
pm: 50,016
في: 28,427
للبيع: 25,777
مطلوب: 23,781
من: 21,241
متر: 18,657
am: 18,568
على: 16,105
للتواصل: 15,189
الحي: 14,868
```

#### Phase 3: Data Extraction
- **Phone Number Extraction**: Multiple regex patterns for various formats
- **Emoji Removal**: Comprehensive Unicode emoji pattern matching
- **Media Reference Cleaning**: Removes "image omitted", "video omitted" patterns
- **Status Keyword Extraction**: Identifies property-related terms (Arabic/English)
- **Region/Area Detection**: AI-powered location extraction from message content

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
| `region` | String | Detected location/area information |
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

## 🗺️ Region/Area Extraction

### Egyptian Cities & Major Areas
- **Major Cities**: القاهرة, الجيزة, الإسكندرية, أسوان, الأقصر
- **New Cities**: العاصمة الإدارية, العبور, بدر, الشروق, الرحاب
- **Special Areas**: النوبارية, وادي النطرون, برج العرب, العلمين

### District/Neighborhood Patterns
- **District Numbers**: `حي \d+`, `الحي \d+` (e.g., حي 19, الحي 32)
- **Neighborhoods**: `مجاورة \d+`, `المجاورة \d+` (e.g., مجاورة 3)
- **Phases**: `المرحلة \d+` (e.g., المرحلة 10)

### Directional & Descriptive Areas
- **Directions**: شمال المدينة, غرب جولف, وسط البلد
- **Extensions**: امتداد غرب, امتداد الجامعات
- **Locations**: في بدر, بمدينة الشروق, ع المترو

## �️ AI-Powered Region Extraction

### Geographic Intelligence System
The `extract_region_names()` function implements advanced AI language processing to automatically detect and extract location information from Arabic and English text. This feature provides valuable geographic intelligence for business analytics.

### Coverage & Scope

#### Egyptian Cities Database
- **Major Cities**: القاهرة, الجيزة, الإسكندرية, أسوان, الأقصر
- **New Cities**: العاصمة الإدارية, العبور, بدر, الشروق, الرحاب
- **Industrial Cities**: العاشر من رمضان, 6 أكتوبر, 15 مايو
- **Coastal Areas**: النوبارية, وادي النطرون, برج العرب, العلمين

#### District & Neighborhood Patterns
- **District Numbers**: `حي \d+`, `الحي \d+` (e.g., حي 19, الحي 32)
- **Neighborhoods**: `مجاورة \d+`, `المجاورة \d+` (e.g., مجاورة 3)
- **Phases**: `المرحلة \d+` (e.g., المرحلة 10)
- **English Variants**: `district \d+`, `neighborhood \d+`

#### Directional & Descriptive Areas
- **Directions**: شمال المدينة, غرب جولف, وسط البلد
- **Extensions**: امتداد غرب, امتداد الجامعات
- **Locations**: في بدر, بمدينة الشروق, ع المترو

### AI Processing Logic

#### Multi-Pattern Recognition
```python
# Geographic patterns detected:
1. City name matching (comprehensive database)
2. Numbered districts (regex: حي \d+)
3. Neighborhoods (regex: مجاورة \d+)
4. Directional areas (شمال/جنوب/شرق/غرب + location)
5. Prepositional phrases (في/بـ + location name)
```

#### Intelligent Filtering
- **Context Awareness**: Filters out property-related terms that aren't locations
- **Length Validation**: Only includes meaningful location names (3+ characters)
- **Noise Reduction**: Removes common words that appear in location context
- **Deduplication**: Maintains unique regions while preserving order

#### Performance Metrics
- **Extraction Rate**: 86.0% of messages contain region information
- **Accuracy**: High precision with comprehensive Egyptian geographic coverage
- **Processing Speed**: Optimized regex patterns for real-time extraction

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

## 🔧 Troubleshooting Guide

### Common Issues & Solutions

#### 1. Empty CSV Output
- **Symptom**: CSV file created but no data rows
- **Cause**: Chat files not found or incorrect path
- **Solution**: Verify `whatsapp_chat_exports/` directory exists and contains `_chat*.txt` files

#### 2. Unicode Errors
- **Symptom**: Garbled text or encoding errors
- **Cause**: File encoding mismatch
- **Solution**: Ensure all files are UTF-8 encoded, check file BOM

#### 3. Memory Issues
- **Symptom**: Script crashes on large files
- **Cause**: Loading all messages into memory at once
- **Solution**: Process files individually, consider streaming approach

#### 4. Phone Number Extraction Issues
- **Symptom**: Valid phone numbers not detected
- **Cause**: New format not covered by regex patterns
- **Solution**: Add pattern to `additional_patterns` list

#### 5. Performance Degradation
- **Symptom**: Very slow processing
- **Cause**: Inefficient regex patterns or large message content
- **Solution**: Profile regex performance, optimize patterns

### Error Codes & Meanings

| Error Type | Description | Action |
|------------|-------------|---------|
| `FileNotFoundError` | Chat files missing | Check file paths |
| `UnicodeDecodeError` | Encoding issue | Verify UTF-8 encoding |
| `MemoryError` | Insufficient RAM | Process smaller batches |
| `RegexError` | Pattern compilation failed | Check regex syntax |

## 🚀 Performance Optimization Tips

### For Large Datasets (100k+ messages):
1. **Batch Processing**: Process files in chunks
2. **Memory Management**: Clear variables after processing
3. **Regex Compilation**: Pre-compile frequently used patterns
4. **Output Streaming**: Write to CSV incrementally

### Example Optimization:
```python
import re
# Pre-compile regex patterns
MOBILE_PATTERN = re.compile(r'(01[0125]\d{8})')
EMOJI_PATTERN = re.compile("[\U0001F600-\U0001F64F"..."]")

# Process in batches
def process_large_file(filename, batch_size=1000):
    batch = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            batch.append(line)
            if len(batch) >= batch_size:
                process_batch(batch)
                batch.clear()
```

##  Testing & Validation

### Unit Test Structure:
```python
def test_phone_extraction():
    test_message = "Contact me at 01234567890"
    result = extract_phone_numbers(test_message)
    assert "01234567890" in result

def test_emoji_removal():
    test_text = "Hello 😊 World 🌍"
    result = remove_emojis(test_text)
    assert result == "Hello  World "

def test_status_keywords():
    test_text = "للبيع شقة جميلة"
    result = extract_status_keywords(test_text)
    assert "للبيع" in result
```

### Data Validation Checklist:
- [ ] All messages have unique IDs
- [ ] Phone numbers follow Egyptian format
- [ ] Status keywords are properly classified
- [ ] Unicode characters preserved
- [ ] CSV headers match data
- [ ] No data corruption in output

---

## 🎯 Quick Reference for AI Agents

### Critical Files:
- `simple_parser.py` - Main processing logic
- `whatsapp_chat_exports/` - Input data directory
- `whatsapp_chats.csv` - Output file

### Key Functions:
- `parse_message()` - Core parsing logic
- `extract_status_keywords()` - Business classification
- `remove_emojis()` - Text cleaning
- `clean_media_references()` - Media cleanup

### Important Variables:
- `all_messages[]` - Main data container
- `headers[]` - CSV column definitions
- `arabic_keywords[]` - Arabic classification terms
- `english_keywords[]` - English classification terms

### Processing Flow:
1. File discovery → 2. Line parsing → 3. Data extraction → 4. Cleaning → 5. CSV export

---

*Last Updated: July 2025*
*Version: 1.0.0*
*Maintainer: AI Development Team*

## 🏠 AI-Powered Property Type Classification

### Overview
The `extract_property_type()` function implements intelligent property classification using comprehensive keyword analysis and contextual AI processing. It automatically categorizes real estate properties into four main types.

### Classification Categories

#### 1. **Apartment** (شقة)
- **Arabic Keywords**: شقة, شقه, الشقة, الشقه, دوبلكس, دوبليكس, بنتهاوس, استوديو, وحدة, وحده
- **English Keywords**: apartment, flat, unit, duplex, penthouse, studio, condo, condominium
- **Context Clues**: Mentions of rooms, floors, building amenities

#### 2. **Villa** (فيلا)
- **Arabic Keywords**: فيلا, فيله, الفيلا, الفيله, قصر, القصر, بيت, البيت, منزل, المنزل, دار, توين هاوس, تاون هاوس
- **English Keywords**: villa, house, mansion, palace, home, residence, townhouse, twin house, standalone
- **Context Clues**: Garden, private entrance, multiple floors

#### 3. **Land** (قطعة أرض)
- **Arabic Keywords**: قطعة, قطعه, ارض, أرض, الارض, الأرض, قطعة ارض, قطعة أرض, مزرعة, المزرعة, فدان
- **English Keywords**: land, plot, lot, piece, farm, acre, ground, site, parcel
- **Context Clues**: Area measurements, construction licenses, building permits

#### 4. **Commercial** (تجاري)
- **Arabic Keywords**: محل, المحل, مكتب, المكتب, عيادة, العيادة, مطعم, المطعم, مقهى, صيدلية, عمارة
- **English Keywords**: shop, store, office, clinic, restaurant, cafe, pharmacy, building, commercial
- **Context Clues**: Business activities, commercial licensing

### AI Processing Logic

#### Multi-Language Detection
```python
# Priority-based matching system:
1. Direct keyword matching (Arabic & English)
2. Contextual analysis for ambiguous cases
3. Priority ranking: Villa > Apartment > Commercial > Land
```

#### Context-Aware Classification
- **Room Detection**: If amenities mentioned → apartment
- **Construction Terms**: If building permits mentioned → land
- **Business Terms**: If commercial activities mentioned → commercial
- **Size References**: Large areas without building type → land

#### Performance Metrics
- **Classification Rate**: 80.8% of all messages
- **Distribution Analysis**:
  - Land: 22,662 messages (48.8%)
  - Apartment: 11,319 messages (24.4%)
  - Villa: 10,330 messages (22.2%)
  - Commercial: 2,153 messages (4.6%)

### Implementation Features

#### Intelligent Priority System
The classifier uses a priority ranking system to handle messages containing multiple property types:
1. **Villa** (most specific residential)
2. **Apartment** (specific residential)
3. **Commercial** (specific non-residential)
4. **Land** (general/undeveloped)

#### Contextual Fallback Logic
```python
# When no direct keywords found:
if rooms/amenities_mentioned:
    return 'apartment'
elif area/construction_mentioned:
    return 'land'
```

#### Quality Assurance
- **False Positive Reduction**: Avoids misclassifying general terms
- **Bilingual Coverage**: Handles Arabic-English mixed content
- **Cultural Adaptation**: Egyptian real estate terminology optimized
