#!/usr/bin/env python3
"""
Debug script to test file reading
"""
import re

def test_file_reading():
    file_path = "/Users/ahmedgomaa/Downloads/pytextai/_chat.txt"
    
    print(f"Testing file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            print(f"Total lines in file: {len(lines)}")
            
            # Test first few lines
            for i, line in enumerate(lines[:10]):
                line = line.strip()
                if not line:
                    continue
                
                print(f"\nLine {i+1}:")
                print(f"Raw: {repr(line)}")
                
                # Clean invisible characters
                cleaned_line = re.sub(r'[\u200e\u200f\u202a-\u202e]', '', line)
                print(f"Cleaned: {repr(cleaned_line)}")
                
                # Test pattern
                pattern = r'^\[(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}:\d{2} (?:AM|PM))\] ([^:]+): (.*)$'
                match = re.match(pattern, cleaned_line)
                
                if match:
                    print("✅ Pattern matched!")
                    print(f"  Date: {match.group(1)}")
                    print(f"  Time: {match.group(2)}")
                    print(f"  Sender: {match.group(3)}")
                    print(f"  Message: {match.group(4)[:50]}...")
                else:
                    print("❌ Pattern didn't match")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_file_reading()
