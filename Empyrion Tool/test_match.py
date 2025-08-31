import re

cleaned_name = "SV505 Warp 10866"  # Example input string

# Remove any extra leading or trailing spaces before attempting the regex match
cleaned_name = cleaned_name.strip()

match = re.search(r'(.*)\s+(\d+)$', cleaned_name)

if match:
    print("Base name:", match.group(1))
    print("Trailing number:", match.group(2))
else:
    print("No match found.")
