import base64
import json

# Read client_secret.json
with open('client_secret.json', 'r') as f:
    client_secret_json = f.read()

# Convert to base64
client_secret_b64 = base64.b64encode(client_secret_json.encode()).decode()

# Save to file
with open('client_secret_base64.txt', 'w') as f:
    f.write(client_secret_b64)

print("✅ Base64 saved to client_secret_base64.txt")
print("\n" + "="*60)
print("COPY THIS VALUE FOR RENDER:")
print("="*60)
print(client_secret_b64)
print("="*60)
