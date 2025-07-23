#!/usr/bin/env python3
import re

# Simulate the message from PRO5
msg = {
    'sender_phone': '',
    'sender_phone_2': '',
    'message': '✍️🔵**شمال المدينة حى7 ع المترو🎢🚦 🏞️ للبيع بمدينة قطعة🌲 بالحى المتميز شمال المدينة ع محطة المترو ،،، ✍️الوصف والتفاصيل كالاتى ق👈طعة 459م شمال المدينة الحى السابع🌿💐 دبل فيس ب🎋حديقة 60م بحرى 🩼 تطل على شارع🚗🚙 حاره خالصة الأقساط وخالصة الاوراق جاهزه على البناء محفوره مطلوب💥💯 سعر مناسب جدا للعملاء بادر بالشراء الان لل👈بيع قطعة459م شمال المدينة الحى السابع بجوار 🎢🚦محطة المترو خالصة الأقساط ومحضر استلام بحرى تتطل ع شارع 4حاره بحديقة خاصة والسعر مميز جدا وأقل من السوق الحق العرض الان وبادر بالاتصال ☎️ ،،،0103147894'
}

print("Original message length:", len(msg['message']))

# First extract the primary number
mobile_pattern = r'(01[0125]\d{8})'
found_numbers = re.findall(mobile_pattern, msg['message'])
print("Primary numbers found:", found_numbers)

if found_numbers:
    if not msg['sender_phone']:
        msg['sender_phone'] = found_numbers[0]
        print("Set sender_phone to:", msg['sender_phone'])
    
    # Remove all found numbers from message
    for num in found_numbers:
        msg['message'] = re.sub(re.escape(num), '', msg['message'])
        print(f"Removed {num} from message")

print("Message after primary extraction:", msg['message'][-100:])  # Last 100 chars

# Now look for additional numbers
additional_patterns = [
    # Numbers at end with commas/special chars like ،،،0103147894
    r'[،,\s]*([01][0125]\d{8})[،,\s]*',
    # Numbers with Arabic-Indic digits (٠١٢٣٤٥٦٧٨٩)
    r'([٠-٩]{11})',
]

for i, pattern in enumerate(additional_patterns):
    matches = re.findall(pattern, msg['message'])
    print(f"Pattern {i+1}: {pattern}")
    print(f"Matches: {matches}")
    
    for match in matches:
        clean_number = match
        
        # Convert Arabic-Indic digits to Western digits
        arabic_to_western = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
        clean_number = clean_number.translate(arabic_to_western)
        
        # Remove all non-digit characters
        clean_number = re.sub(r'[^\d]', '', clean_number)
        
        print(f"Clean number: {clean_number}")
        print(f"Length: {len(clean_number)}")
        print(f"Starts with valid prefix: {clean_number.startswith(('010', '011', '012', '015'))}")
        print(f"Different from sender_phone: {clean_number != msg['sender_phone']}")
        print(f"sender_phone_2 is empty: {not msg['sender_phone_2']}")
        
        # Check if it's a valid Egyptian mobile number
        if (len(clean_number) == 11 and 
            clean_number.startswith(('010', '011', '012', '015')) and
            clean_number != msg['sender_phone'] and 
            not msg['sender_phone_2']):
            
            msg['sender_phone_2'] = clean_number
            print(f"✅ Set sender_phone_2 to: {clean_number}")
            
            # Remove the original match from message
            original_pattern = re.escape(match)
            msg['message'] = re.sub(r'[،,\s]*' + original_pattern + r'[،,\s]*', ' ', msg['message'])
            print(f"Removed {match} from message")
            break
        else:
            print("❌ Number not valid or conditions not met")

print(f"\nFinal result:")
print(f"sender_phone: {msg['sender_phone']}")
print(f"sender_phone_2: {msg['sender_phone_2']}")
print(f"Message end: {msg['message'][-50:]}")
