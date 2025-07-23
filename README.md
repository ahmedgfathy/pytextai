# 💬 WhatsApp Chat Parser & Data Extraction System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)
![Platform](https://img.shields.io/badge/Platform-Cross%20Platform-lightgrey.svg)

*🚀 Transform WhatsApp group chat exports into structured business intelligence data*

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Usage](#-usage)
- [Output Format](#-output-format)
- [Technical Stack](#-technical-stack)
- [Project Structure](#-project-structure)
- [Performance](#-performance)
- [Contributing](#-contributing)
- [License](#-license)

## 🎯 Overview

This **WhatsApp Chat Parser** is a powerful Python-based system designed to extract valuable business intelligence from WhatsApp group chat exports. It transforms raw chat .txt files into clean, structured CSV data suitable for analysis, lead generation, and business insights.

### 🏢 Business Use Cases
- **Real Estate Analytics**: Extract property listings, prices, and contact information
- **Lead Generation**: Identify potential customers and their contact details
- **Market Research**: Analyze conversation patterns and business trends
- **Data Mining**: Clean and structure unorganized chat data for BI tools

## ✨ Features

### 🧹 **Advanced Text Processing**
- **Unicode Normalization**: Handles Arabic, English, and mixed-language content
- **Emoji Removal**: Comprehensive emoji cleaning using Unicode patterns
- **Media Reference Cleaning**: Removes "image omitted", "video omitted" patterns
- **Multi-line Message Handling**: Properly concatenates split messages

### 📱 **Smart Phone Number Extraction**
- **Multiple Format Support**: Egyptian mobile, international (+20), Arabic-Indic digits
- **Dual Phone Detection**: Primary and secondary phone numbers per message
- **Flexible Pattern Matching**: Handles spaces, dashes, dots in phone numbers
- **Validation**: Ensures extracted numbers are valid Egyptian mobile numbers

### 🏷️ **Intelligent Classification**
- **Property Status Keywords**: Detects sale, rent, wanted, investment terms
- **Bilingual Support**: Arabic and English keyword recognition
- **Status Extraction**: Automatically categorizes messages by business intent

### 📊 **Data Structuring**
- **Unique ID Generation**: Sequential PRO1, PRO2, ... identifiers
- **Message Backup**: Preserves original content before cleaning
- **Metadata Tracking**: Source file, line numbers, timestamps
- **Statistical Analysis**: Processing summary and insights

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/whatsapp-chat-parser.git
cd whatsapp-chat-parser
```

### 2. Prepare Your Data
Place your WhatsApp chat export .txt files in the `whatsapp_chat_exports/` folder:
```
whatsapp_chat_exports/
├── _chat.txt
├── _chat 2.txt
└── _chat 3.txt
```

### 3. Run the Parser
```bash
python3 simple_parser.py
```

### 4. Get Results
Find your structured data in `whatsapp_chats.csv` with comprehensive statistics:
```
🔍 WhatsApp Chat Parser - Simple Version
==================================================
Found 14 chat files
Processing: whatsapp_chat_exports/_chat.txt
  - Extracted 2648 messages
...
✅ CSV saved: whatsapp_chats.csv
📊 Statistics:
  - Total messages: 57,488
  - Messages with phone numbers: 45,077
  - Messages with status keywords: 47,496
  - Unique senders: 478
```

## 🔧 Installation

### Prerequisites
- **Python 3.8+** (recommended)
- No external dependencies required (uses Python standard library only)

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/whatsapp-chat-parser.git
cd whatsapp-chat-parser

# No additional installation needed - uses Python standard library only!
```

## 💻 Usage

### Basic Usage
```bash
python3 simple_parser.py
```

### Advanced Configuration
Customize keyword extraction by modifying the `extract_status_keywords()` function in `simple_parser.py`:

```python
# Add custom Arabic keywords
arabic_keywords = [
    'للبيع', 'مطلوب', 'معروض', 'ايجار',
    'your_custom_keyword'  # Add here
]

# Add custom English keywords
english_keywords = [
    'for sale', 'wanted', 'available', 'rent',
    'your_custom_keyword'  # Add here
]
```

## 📄 Output Format

The system generates a comprehensive CSV file with the following structure:

| Column | Description | Example |
|--------|-------------|---------|
| `unique_id` | Sequential identifier | PRO1, PRO2, PRO3... |
| `file_source` | Source chat file | whatsapp_chat_exports/_chat.txt |
| `date` | Message date | 24/05/2025 |
| `time` | Message time | 1:04:06 AM |
| `sender_name` | Cleaned sender name | Ahmed Gomaa |
| `sender_phone` | Primary phone number | 01234567890 |
| `sender_phone_2` | Secondary phone number | 01098765432 |
| `message` | Cleaned message content | للبيع شقة 120 متر... |
| `message_backup` | Original message | 🏠للبيع شقة 120 متر📱01234567890 |
| `status` | Extracted keywords | للبيع, for sale |
| `line_number` | Source line number | 150 |

### 📊 Sample Output
```csv
unique_id,file_source,date,time,sender_name,sender_phone,sender_phone_2,message,message_backup,status,line_number
PRO1,whatsapp_chat_exports/_chat.txt,24/05/2025,1:04:06 AM,Ahmed Gomaa,01234567890,,للبيع شقة 120 متر,🏠للبيع شقة 120 متر📱01234567890,للبيع,45
PRO2,whatsapp_chat_exports/_chat.txt,24/05/2025,2:15:30 PM,Sara Ali,01098765432,01155443322,مطلوب شقة للايجار,مطلوب شقة للايجار 📞01155443322,مطلوب,78
```

## 🛠️ Technical Stack

### **Programming Language**
- ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) **Python 3.8+**

### **Core Libraries**
- `re` - Advanced regex pattern matching
- `csv` - Structured data export
- `glob` - File discovery and pattern matching
- `os` - System operations

### **Key Technologies**
- **Unicode Processing**: Full Arabic/English text support
- **Regex Engineering**: Optimized patterns for phone/keyword extraction
- **CSV Export**: UTF-8 encoded structured output
- **Statistical Analysis**: Real-time processing metrics

## 📁 Project Structure

```
whatsapp-chat-parser/
├── 📄 simple_parser.py           # Main processing script
├── 📁 whatsapp_chat_exports/     # Raw chat files directory
│   ├── _chat.txt
│   ├── _chat 2.txt
│   └── ... (multiple files)
├── 📊 whatsapp_chats.csv         # Generated output
├── 📋 requirements.txt           # Dependencies (minimal)
├── 📖 README.md                  # This documentation
├── 🛠️ TECHNICAL.md              # Technical implementation guide
└── 📄 .gitignore                # Git ignore patterns
```

## ⚡ Performance

### **Processing Capabilities**
- **Volume**: 50,000+ messages processed in under 60 seconds
- **Accuracy**: 78%+ phone number extraction rate
- **Classification**: 82%+ status keyword detection rate
- **Memory**: Efficient processing with moderate memory usage

### **Scalability Metrics**
- **Files**: Handles 10+ chat files simultaneously
- **Size**: Processes files up to 50MB+ efficiently
- **Languages**: Full Arabic/English bilingual support
- **Formats**: Multiple phone number format recognition

## 🔍 Key Features Showcase

### 🎯 **Smart Phone Number Detection**
```python
# Handles multiple formats:
# 01234567890, +20 123 456 7890, ٠١٢٣٤٥٦٧٨٩٠
# 010 1234 5678, 0101-234-5678, etc.
```

### 🏷️ **Intelligent Keyword Classification**
```python
# Arabic: للبيع, مطلوب, معروض, ايجار, للاستثمار
# English: for sale, wanted, available, rent, investment
```

### 🧹 **Advanced Text Cleaning**
```python
# Removes: Emojis, Media references, Deleted messages
# Preserves: Original content in backup field
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🐛 **Bug Reports**
- Open an issue with detailed reproduction steps
- Include sample data (anonymized)
- Specify your Python version and OS

### 🚀 **Feature Requests**
- Describe the use case and expected behavior
- Provide examples of desired input/output
- Explain business value and impact

### 💻 **Code Contributions**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Commit your changes (`git commit -m 'Add amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### 📋 **Development Guidelines**
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include test cases for new features
- Update documentation as needed

## 📞 Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/whatsapp-chat-parser/issues)
- **Documentation**: [Technical Guide](TECHNICAL.md)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/whatsapp-chat-parser/discussions)

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ for the data science and business intelligence community**

⭐ **Star this repo if it helped you!** ⭐

</div>
