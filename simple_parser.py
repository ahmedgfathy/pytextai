#!/usr/bin/env python3
"""
Simple WhatsApp Chat Parser
"""

import os
import re
import csv
import glob

def clean_line(line):
    """Clean Unicode characters from line"""
    line = re.sub(r'[\u200e\u200f\u202a-\u202f\xa0]', ' ', line.strip())
    line = re.sub(r' +', ' ', line)
    return line

def parse_message(line):
    """Parse a message line"""
    pattern = r'^\[(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}:\d{2} (?:AM|PM))\] ([^:]+): (.*)$'
    match = re.match(pattern, line)
    
    if match:
        date = match.group(1)
        time = match.group(2)
        sender = match.group(3).strip()
        message = match.group(4).strip()
        
        # Extract phone
        phone_pattern = r'\+(\d{2} \d{3} \d{3} \d{4})'
        phone_match = re.search(phone_pattern, sender)
        
        if phone_match:
            phone = '+' + phone_match.group(1).replace(' ', '')
            name = "Unknown"
        else:
            phone = ""
            name = sender[2:].strip() if sender.startswith('~ ') else sender.strip()
        
        return {
            'date': date,
            'time': time,
            'sender_name': name,
            'sender_phone': phone,
            'message': message
        }
    return None

def main():
    print("🔍 WhatsApp Chat Parser - Simple Version")
    print("=" * 50)
    
    # Find chat files
    files = glob.glob("_chat*.txt")
    print(f"Found {len(files)} chat files")
    
    all_messages = []
    
    for filename in files:
        print(f"Processing: {filename}")
        count = 0
        current_msg = None
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue
                    
                    cleaned = clean_line(line)
                    parsed = parse_message(cleaned)
                    
                    if parsed:
                        if current_msg:
                            all_messages.append(current_msg)
                        current_msg = parsed
                        current_msg['file_source'] = filename
                        current_msg['line_number'] = line_num
                        count += 1
                    else:
                        if current_msg:
                            current_msg['message'] += ' ' + line.strip()
                
                if current_msg:
                    all_messages.append(current_msg)
                    
            print(f"  - Extracted {count} messages")
            
        except Exception as e:
            print(f"  - Error: {e}")
    
    print(f"\nTotal messages: {len(all_messages)}")
    
    if all_messages:
        # Add unique ID and extract mobile numbers from messages
        mobile_pattern = r'(01[0125]\d{8})'
        
        for i, msg in enumerate(all_messages, 1):
            # Add unique ID
            msg['unique_id'] = f"PRO{i}"
            
            # Extract mobile numbers from message content
            found_numbers = re.findall(mobile_pattern, msg['message'])
            if found_numbers:
                # If sender_phone is empty, set to first found number
                if not msg['sender_phone']:
                    msg['sender_phone'] = found_numbers[0]
                
                # Remove all found numbers from message
                for num in found_numbers:
                    msg['message'] = re.sub(re.escape(num), '', msg['message'])
                
                # Clean up extra spaces and punctuation
                msg['message'] = re.sub(r'[.\s]+', ' ', msg['message']).strip()
        
        # Save to CSV
        headers = ['unique_id', 'file_source', 'date', 'time', 'sender_name', 'sender_phone', 'message', 'line_number']
        with open('whatsapp_chats.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_messages)
        print(f"✅ CSV saved: whatsapp_chats.csv")
        
        # Show statistics
        phone_count = sum(1 for msg in all_messages if msg['sender_phone'])
        print(f"📊 Statistics:")
        print(f"  - Total messages: {len(all_messages)}")
        print(f"  - Messages with phone numbers: {phone_count}")
        print(f"  - Unique senders: {len(set(msg['sender_name'] for msg in all_messages))}")
        
        # Show sample
        print("\n📋 Sample messages:")
        for i, msg in enumerate(all_messages[:3]):
            phone_display = f" ({msg['sender_phone']})" if msg['sender_phone'] else ""
            print(f"{i+1}. {msg['unique_id']} - [{msg['date']} {msg['time']}] {msg['sender_name']}{phone_display}: {msg['message'][:50]}...")
    else:
        print("❌ No messages found")

if __name__ == "__main__":
    main()
