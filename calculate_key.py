import base64

def add_padding(s):
    return s + '=' * (-len(s) % 4)

try:
    # Part 1: Username (Base64 encoded by user?)
    user_part_b64 = "bnN1YnVnYWNvbGxpbkBnbWFpbC5jb20"
    user_part_b64_padded = add_padding(user_part_b64)
    decoded_user = base64.b64decode(user_part_b64_padded).decode('utf-8')
    print(f"Decoded username: {decoded_user}")
    
    # Part 2: Password
    password_part = "M21ye8rOIk5vlxy2Dko70"
    
    # Combine for Basic Auth
    raw_creds = f"{decoded_user}:{password_part}"
    print(f"Raw credentials: {raw_creds}")
    
    # Encode for Header
    encoded_key = base64.b64encode(raw_creds.encode('utf-8')).decode('utf-8')
    print(f"FINAL_DID_KEY: {encoded_key}")

except Exception as e:
    print(f"Error: {e}")
