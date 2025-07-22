import re

# Test line from the file
test_line = "[10/06/2025, 5:22:03 AM] ✨🎗️شركه السويفي العقاريه  🎗️✨: ‎Messages and calls are end-to-end encrypted. Only people in this chat can read, listen to, or share them."

print("Original line:")
print(repr(test_line))
print()

# Clean invisible characters
cleaned_line = re.sub(r'[\u200e\u200f\u202a-\u202e]', '', test_line.strip())
print("Cleaned line:")
print(repr(cleaned_line))
print()

# Test pattern
pattern = r'^\[(\d{2}/\d{2}/\d{4}), (\d{1,2}:\d{2}:\d{2} (?:AM|PM))\] ([^:]+): (.*)$'
match = re.match(pattern, cleaned_line)

print("Pattern match:")
if match:
    print("✅ Match found!")
    print(f"Date: {match.group(1)}")
    print(f"Time: {match.group(2)}")
    print(f"Sender: {match.group(3)}")
    print(f"Message: {match.group(4)}")
else:
    print("❌ No match")
    print("Testing simpler pattern...")
    # Try to find what's at the start
    bracket_pattern = r'^\[([^\]]+)\] ([^:]+): (.*)$'
    simple_match = re.match(bracket_pattern, cleaned_line)
    if simple_match:
        print(f"✅ Simple pattern matched!")
        print(f"DateTime: {simple_match.group(1)}")
        print(f"Sender: {simple_match.group(2)}")
        print(f"Message: {simple_match.group(3)}")
    else:
        print("❌ Even simple pattern failed")
