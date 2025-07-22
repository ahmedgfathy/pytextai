# WhatsApp Chat Parser

A Python script to parse WhatsApp group chat export files and convert them into CSV format for easy analysis.

## Features

- 📱 Parses WhatsApp chat export files (.txt format)
- 📊 Extracts sender names, phone numbers, timestamps, and messages
- 📝 Outputs data to CSV format with proper column headers
- 🔍 Handles multi-line messages and various sender formats
- 📈 Provides statistics about the parsed data
- 🌍 Supports Unicode/Arabic text

## How to Use

1. **Export WhatsApp Chats**: 
   - Open WhatsApp group
   - Go to Settings → Export Chat → Without Media
   - Save the exported .txt files in this folder

2. **Run the Parser**:
   ```bash
   python whatsapp_chat_parser.py
   ```

3. **Output**: 
   - The script will create `whatsapp_chats.csv` with all parsed messages

## CSV Output Columns

| Column | Description |
|--------|-------------|
| `file_source` | Original chat file name |
| `date` | Message date (DD/MM/YYYY) |
| `time` | Message time (HH:MM:SS AM/PM) |
| `sender_name` | Sender's display name |
| `sender_phone` | Sender's phone number (if available) |
| `message` | The actual message content |
| `line_number` | Line number in original file |

## Supported Message Formats

The parser handles these WhatsApp export formats:
- `[10/06/2025, 5:22:03 AM] John Doe: Hello everyone`
- `[10/06/2025, 5:22:03 AM] ‪+20 103 011 4411‬: Message from phone number`
- `[10/06/2025, 5:22:03 AM] ~ DisplayName: Message with tilde prefix`

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only built-in libraries)

## Example Usage

```python
from whatsapp_chat_parser import WhatsAppChatParser

# Initialize parser
parser = WhatsAppChatParser("/path/to/chat/files")

# Process all .txt files
parser.process_all_files()

# Save to CSV
parser.save_to_csv("my_chats.csv")

# Get statistics
stats = parser.get_statistics()
print(f"Processed {stats['total_messages']} messages")
```

## Troubleshooting

**No messages extracted?**
- Check that your .txt files are WhatsApp exports
- Ensure files are in UTF-8 encoding
- Verify the date/time format matches WhatsApp exports

**Missing phone numbers?**
- Phone numbers are only extracted when users haven't set display names
- Display names take precedence over phone numbers in WhatsApp

**Unicode/Arabic text issues?**
- The script handles UTF-8 encoding automatically
- Make sure your terminal supports Unicode display
