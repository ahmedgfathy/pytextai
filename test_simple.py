#!/usr/bin/env python3
import re
import glob
import os

def test_parsing():
    print("🔍 Testing WhatsApp Chat Parser")
    print("=" * 50)
    
    # Find files
    txt_files = glob.glob("_chat*.txt")
    print(f"Found {len(txt_files)} files")
    
    if not txt_files:
        print("No files found!")
        return
    
    # Test first file
    file_path = txt_files[0]
    print(f"Testing file: {file_path}")
    
    message_count = 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                if line_num > 10:  # Test only first 10 lines
                    break
                    
                line = line.strip()
                if not line:
                    continue
                
                print(f"\nLine {line_num}: {repr(line[:100])}")
                
                # Clean Unicode
                cleaned = re.sub(r'[\u200e\u200f\u202a-\u202f\xa0]', ' ', line)
                cleaned = re.sub(r' +', ' ', cleaned)
                
                # Test pattern
                pattern = r'^\[(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}:\d{2} (?:AM|PM))\] ([^:]+): (.*)$'
                match = re.match(pattern, cleaned)
                
                if match:
                    message_count += 1
                    print(f"✅ MATCH! Date: {match.group(1)}, Sender: {match.group(3)[:30]}")
                else:
                    print("❌ No match")
        
        print(f"\nFound {message_count} messages in first 10 lines")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_parsing()
