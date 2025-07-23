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

def remove_emojis(text):
    """Remove all emojis from text"""
    # Emoji pattern - covers most emoji ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese char
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def clean_media_references(text):
    """Remove media references like 'image omitted', 'video omitted' with timestamps"""
    # Remove patterns like "‎[24/05/2025, 6:22:15 PM] ~ sender: ‎image omitted"
    media_pattern1 = r'‎\[\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} (?:AM|PM)\] [^:]*: ‎(?:image|video) omitted'
    text = re.sub(media_pattern1, '', text)
    
    # Remove patterns like "‎[24/05/2025, 6:22:15 PM] ‪+20 XXX XXX XXXX‬: ‎image omitted"
    media_pattern2 = r'‎\[\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} (?:AM|PM)\] ‪[^‬]*‬: ‎(?:image|video) omitted'
    text = re.sub(media_pattern2, '', text)
    
    # Remove patterns without Unicode markers - more general
    media_pattern3 = r'\[\d{2}/\d{2}/\d{4}, \d{1,2}:\d{2}:\d{2} (?:AM|PM)\] [^:]*: (?:image|video) omitted'
    text = re.sub(media_pattern3, '', text)
    
    # Remove standalone media omitted text
    media_pattern4 = r'(?:image|video) omitted'
    text = re.sub(media_pattern4, '', text, flags=re.IGNORECASE)
    
    # Remove "This message can't be displayed here. Please open WhatsApp on your phone to view the message."
    whatsapp_pattern = r'This message can\'t be displayed here\.?\s*Please open .*?WhatsApp.*? on your phone to view the message\.?'
    text = re.sub(whatsapp_pattern, '', text, flags=re.IGNORECASE)
    
    # Remove "This message was deleted" patterns
    deleted_pattern = r'This message was deleted\.?'
    text = re.sub(deleted_pattern, '', text, flags=re.IGNORECASE)
    
    return text

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
            'sender_phone_2': '',
            'message': message,
            'message_backup': message,
            'status': '',
            'region': ''
        }
    return None

def extract_status_keywords(text):
    """Extract property status keywords from text"""
    # Arabic keywords
    arabic_keywords = [
        'للبيع', 'للبيع:', 'بيع', 'بيع:', 
        'مطلوب', 'مطلوب:', 
        'معروض', 'معروض:', 
        'ايجار', 'للايجار', 'للايجار:', 'ايجار:', 'للإيجار',
        'للاستثمار', 'استثمار', 'تاجير', 'تأجير'
    ]
    
    # English keywords
    english_keywords = [
        'for sale', 'sale', 'selling', 'sell',
        'wanted', 'required', 'looking for',
        'offered', 'available', 'offering',
        'rent', 'rental', 'for rent', 'renting',
        'lease', 'leasing', 'investment'
    ]
    
    found_keywords = []
    text_lower = text.lower()
    
    # Search for Arabic keywords
    for keyword in arabic_keywords:
        if keyword in text:
            found_keywords.append(keyword)
    
    # Search for English keywords
    for keyword in english_keywords:
        if keyword in text_lower:
            found_keywords.append(keyword)
    
    # Return unique keywords joined by comma
    return ', '.join(list(dict.fromkeys(found_keywords)))  # Remove duplicates while preserving order

def extract_region_names(text):
    """Extract region/area names from message text using AI language processing"""
    
    # Egyptian cities and major areas
    egyptian_cities = [
        # Major cities
        'القاهرة', 'cairo', 'الجيزة', 'giza', 'الإسكندرية', 'alexandria', 'أسوان', 'aswan',
        'الأقصر', 'luxor', 'المنصورة', 'mansoura', 'طنطا', 'tanta', 'الزقازيق', 'zagazig',
        'بورسعيد', 'port said', 'السويس', 'suez', 'الإسماعيلية', 'ismailia',
        
        # New Administrative Capital and new cities
        'العاصمة الإدارية', 'العاصمة الجديدة', 'العاصمة الادارية', 'administrative capital', 'new capital',
        'العبور', 'el obour', 'obour', 'مدينة العبور', 'العبور الجديدة', 'new obour',
        'بدر', 'badr', 'مدينة بدر', 'badr city', 'مدينة المستقبل', 'city of the future',
        'الشروق', 'el shorouk', 'shorouk', 'مدينة الشروق', 'shorouk city',
        'الرحاب', 'rehab', 'مدينة الرحاب', 'rehab city', 'التجمع', 'new cairo', 'التجمع الخامس',
        'مدينة نصر', 'nasr city', 'المقطم', 'mokattam', 'المعادي', 'maadi',
        
        # 10th of Ramadan and surrounding areas
        'العاشر من رمضان', '10th of ramadan', 'th10 of ramadan', 'العاشر', 'ramadan city',
        '15 مايو', '15 may', 'مدينة 15 مايو', '6 أكتوبر', '6th october', 'october city',
        
        # Specific areas in new cities
        'النوبارية', 'el nobariya', 'nobariya', 'وادي النطرون', 'wadi el natrun',
        'برج العرب', 'borg el arab', 'العلمين', 'el alamein', 'alamein',
        
        # Districts and neighborhoods (حي)
        'حي', 'حى', 'district', 'الحي', 'الحى'
    ]
    
    # Neighborhood/district patterns (مجاورة)
    neighborhood_patterns = [
        'مجاورة', 'مجاوره', 'neighborhood', 'المجاورة', 'المجاوره'
    ]
    
    # Compass directions and locations
    directions = [
        'شمال', 'north', 'جنوب', 'south', 'شرق', 'east', 'غرب', 'west',
        'شمالي', 'شمالى', 'جنوبي', 'جنوبى', 'شرقي', 'شرقى', 'غربي', 'غربى',
        'وسط', 'center', 'central', 'downtown'
    ]
    
    # Area-specific terms
    area_terms = [
        'منطقة', 'area', 'المنطقة', 'نطاق', 'إقليم', 'region', 'المدينة', 'city',
        'القرية', 'village', 'البلد', 'town', 'الضاحية', 'suburb', 'امتداد', 'extension'
    ]
    
    found_regions = []
    text_lower = text.lower()
    
    # Extract Egyptian cities and areas
    for city in egyptian_cities:
        if city.lower() in text_lower:
            found_regions.append(city)
    
    # Extract neighborhood patterns with numbers (e.g., "حي 19", "مجاورة 3")
    neighborhood_patterns_regex = [
        r'(?:حي|حى|الحي|الحى)\s*(\d+)',  # حي 19, الحي 22
        r'(?:مجاورة|مجاوره|المجاورة|المجاوره)\s*(\d+)',  # مجاورة 3, المجاورة 81
        r'(?:district|neighborhood)\s*(\d+)',  # district 15
        r'(?:المرحله|المرحلة)\s*\(?\s*(\d+)\s*\)?',  # المرحله (10)
    ]
    
    for pattern in neighborhood_patterns_regex:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if 'حي' in pattern or 'حى' in pattern:
                found_regions.append(f"حي {match}")
            elif 'مجاور' in pattern:
                found_regions.append(f"مجاورة {match}")
            elif 'district' in pattern:
                found_regions.append(f"District {match}")
            elif 'المرحل' in pattern:
                found_regions.append(f"المرحلة {match}")
    
    # Extract areas with directions (e.g., "شمال المدينة", "غرب جولف")
    direction_patterns = [
        r'(شمال|جنوب|شرق|غرب|وسط)\s+([^\s،,]{3,15})',  # شمال المدينة
        r'(north|south|east|west|central)\s+([^\s،,]{3,15})',  # north cairo
        r'امتداد\s+([^\s،,]{3,15})',  # امتداد غرب
    ]
    
    for pattern in direction_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                if len(match) == 2:
                    found_regions.append(f"{match[0]} {match[1]}")
                else:
                    found_regions.append(' '.join(match))
            else:
                found_regions.append(f"امتداد {match}")
    
    # Extract specific location names (potential areas/landmarks)
    # Look for patterns like "في X" where X could be a location
    location_patterns = [
        r'(?:في|ف|بـ|ب)\s+([أ-ي\w]{3,20})',  # في بدر, ف الشروق
        r'(?:in|at)\s+([a-zA-Z]{3,20})',  # in Badr, at Shorouk
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Filter out common words that aren't locations
            if match.lower() not in ['الحي', 'حي', 'مجاورة', 'مجاوره', 'المجاورة', 'المجاوره', 
                                   'البيت', 'الشقة', 'العقار', 'المنزل', 'الفيلا', 'house', 'apartment',
                                   'property', 'villa', 'building', 'floor', 'room', 'meter', 'متر',
                                   'ادوار', 'دور', 'غرفة', 'صالة', 'مطبخ', 'حمام']:
                if len(match) >= 3:  # Only include meaningful location names
                    found_regions.append(match)
    
    # Clean and deduplicate regions
    cleaned_regions = []
    for region in found_regions:
        region = region.strip()
        if region and len(region) >= 2:
            cleaned_regions.append(region)
    
    # Remove duplicates while preserving order
    unique_regions = list(dict.fromkeys(cleaned_regions))
    
    # Limit to most relevant regions (max 3 to avoid noise)
    return ', '.join(unique_regions[:3]) if unique_regions else ''

def main():
    print("🔍 WhatsApp Chat Parser - Simple Version")
    print("=" * 50)
    
    # Find chat files
    files = glob.glob("whatsapp_chat_exports/_chat*.txt")
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
                            current_msg['message_backup'] += ' ' + line.strip()
                
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
                # If sender_phone is empty, set to first found number only
                if not msg['sender_phone']:
                    msg['sender_phone'] = found_numbers[0]
                
                # Remove all found numbers from message
                for num in found_numbers:
                    msg['message'] = re.sub(re.escape(num), '', msg['message'])
                
                # Clean up extra spaces and punctuation
                msg['message'] = re.sub(r'[.\s]+', ' ', msg['message']).strip()
            
            # Look for additional mobile numbers with various formats
            additional_patterns = [
                # 10-digit numbers like 0103147894 (common shortened format)
                r'[،,\s]*([01]\d{9})[،,\s]*',
                # Numbers at end with commas/special chars like ،،،0103147894
                r'[،,\s]*([01][0125]\d{8})[،,\s]*',
                # Numbers with Arabic-Indic digits (٠١٢٣٤٥٦٧٨٩)
                r'([٠-٩]{10,11})',
                # Numbers in embedded messages like +20 109 199 2423 (with Unicode chars)
                r'[\u200a\u202a]*\+20\s*(\d{3})\s*(\d{3})\s*(\d{4})[\u202c]*',
                # Flexible pattern with spaces/dots/dashes
                r'(01[0125][\s\-\.\u00A0]*\d[\s\-\.\u00A0]*\d[\s\-\.\u00A0]*\d[\s\-\.\u00A0]*\d[\s\-\.\u00A0]*\d[\s\-\.\u00A0]*\d[\s\-\.\u00A0]*\d[\s\-\.\u00A0]*\d)',
                # Numbers with spaces like 010 6306 6855
                r'([01][0125]\d[\s]*\d{3}[\s]*\d{4})',
            ]
            
            for pattern in additional_patterns:
                matches = re.findall(pattern, msg['message'])
                for match in matches:
                    if isinstance(match, tuple):  # For patterns with groups
                        if len(match) == 3:  # +20 xxx xxx xxxx format
                            clean_number = '0' + ''.join(match)  # Convert +20 109 199 2423 to 01091992423
                        else:
                            clean_number = ''.join(match)
                    else:
                        clean_number = match
                    
                    # Convert Arabic-Indic digits to Western digits
                    arabic_to_western = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
                    clean_number = clean_number.translate(arabic_to_western)
                    
                    # Remove all non-digit characters
                    clean_number = re.sub(r'[^\d]', '', clean_number)
                    
                    # Check if it's a valid Egyptian mobile number (10 or 11 digits)
                    # Egyptian mobile prefixes: 010, 011, 012, 015, 0100, 0101, 0102, 0106, 0109
                    if (len(clean_number) >= 10 and len(clean_number) <= 11 and
                        (clean_number.startswith(('010', '011', '012', '015', '0100', '0101', '0102', '0106', '0109')) or 
                         (len(clean_number) == 10 and clean_number.startswith(('01')))) and
                        clean_number != msg['sender_phone'] and 
                        not msg['sender_phone_2']):
                        msg['sender_phone_2'] = clean_number
                        
                        # Remove the original match from message
                        if isinstance(match, tuple):
                            if len(match) == 3:
                                # For +20 format, remove the whole pattern
                                msg['message'] = re.sub(r'[\u200a\u202a]*\+20\s*' + re.escape(match[0]) + r'\s*' + re.escape(match[1]) + r'\s*' + re.escape(match[2]) + r'[\u202c]*', '', msg['message'])
                            else:
                                original_pattern = re.escape(''.join(match))
                                msg['message'] = re.sub(original_pattern, '', msg['message'])
                        else:
                            # For single match, try to remove with surrounding chars
                            original_pattern = re.escape(match)
                            msg['message'] = re.sub(r'[،,\s]*' + original_pattern + r'[،,\s]*', ' ', msg['message'])
                            msg['message'] = re.sub(original_pattern, '', msg['message'])
                        
                        break  # Only take the first valid number found
            
            # Clean up extra spaces and punctuation
            msg['message'] = re.sub(r'[.\s]+', ' ', msg['message']).strip()
            
            # Remove emojis and media references from both message and message_backup
            msg['message'] = remove_emojis(msg['message'])
            msg['message'] = clean_media_references(msg['message'])
            
            # Extract status keywords from message_backup (original message)
            msg['status'] = extract_status_keywords(msg['message_backup'])
            
            # Extract region names from message_backup (original message)
            msg['region'] = extract_region_names(msg['message_backup'])
            
            # Also clean sender_name from emojis
            msg['sender_name'] = remove_emojis(msg['sender_name'])
            
            # Final cleanup - remove extra spaces
            msg['message'] = re.sub(r'\s+', ' ', msg['message']).strip()
            msg['sender_name'] = re.sub(r'\s+', ' ', msg['sender_name']).strip()
        
        # Save to CSV
        headers = ['unique_id', 'file_source', 'date', 'time', 'sender_name', 'sender_phone', 'sender_phone_2', 'message', 'message_backup', 'status', 'region', 'line_number']
        with open('whatsapp_chats.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(all_messages)
        print(f"✅ CSV saved: whatsapp_chats.csv")
        
        # Show statistics
        phone_count = sum(1 for msg in all_messages if msg['sender_phone'])
        phone2_count = sum(1 for msg in all_messages if msg['sender_phone_2'])
        status_count = sum(1 for msg in all_messages if msg['status'])
        region_count = sum(1 for msg in all_messages if msg['region'])
        print(f"📊 Statistics:")
        print(f"  - Total messages: {len(all_messages)}")
        print(f"  - Messages with phone numbers: {phone_count}")
        print(f"  - Messages with second phone numbers: {phone2_count}")
        print(f"  - Messages with status keywords: {status_count}")
        print(f"  - Messages with region information: {region_count}")
        print(f"  - Unique senders: {len(set(msg['sender_name'] for msg in all_messages))}")
        
        # Show sample
        print("\n📋 Sample messages:")
        for i, msg in enumerate(all_messages[:5]):
            phone_display = f" ({msg['sender_phone']})" if msg['sender_phone'] else ""
            phone2_display = f" + {msg['sender_phone_2']}" if msg['sender_phone_2'] else ""
            region_display = f" [📍{msg['region']}]" if msg['region'] else ""
            print(f"{i+1}. {msg['unique_id']} - [{msg['date']} {msg['time']}] {msg['sender_name']}{phone_display}{phone2_display}{region_display}: {msg['message'][:50]}...")
    else:
        print("❌ No messages found")

if __name__ == "__main__":
    main()
