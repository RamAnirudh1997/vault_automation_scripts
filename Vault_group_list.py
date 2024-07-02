import hvac
import csv


# try:
#     with open(VAULT_TOKEN_PATH, 'r') as token_file:
#         vault_token = token_file.read().strip()
# except FileNotFoundError:
#     print(f"Vault token file not found at {VAULT_TOKEN_PATH}. Make sure you have logged in using Vault CLI.")
#     exit(1)

# Configuration - Replace these with your actual Vault details
VAULT_URL = 'http://127.0.0.1:8200'  # Your Vault server URL
ROLE_ID = 'your-approle-role-id'      # Your AppRole Role ID
SECRET_ID = 'your-approle-secret-id'  # Your AppRole Secret ID

# Initialize the Vault client
client = hvac.Client(url=VAULT_URL)

# Authenticate with AppRole
try:
    auth_response = client.auth.approle.login(
        role_id=ROLE_ID,
        secret_id=SECRET_ID
    )
    client.token = auth_response['auth']['client_token']
except hvac.exceptions.Forbidden:
    print("AppRole authentication failed. Please check your Role ID and Secret ID.")
    exit(1)
except hvac.exceptions.InvalidRequest as e:
    print(f"AppRole authentication error: {e}")
    exit(1)

# Check if the client is authenticated
if not client.is_authenticated():
    print("Authentication failed. Please check your AppRole credentials.")
    exit(1)

# Retrieve the list of groups
try:
    response = client.secrets.identity.list_groups()
    groups = response['data']['key_info']
except hvac.exceptions.InvalidPath:
    print("Failed to retrieve groups. Make sure your Vault setup and path are correct.")
    exit(1)

filename = 'group_policies.csv'

# Open the CSV file for writing
with open(filename, 'w', newline='') as csvfile:
    # Define the fieldnames for the CSV file
    fieldnames = ['GroupName', 'Policies']
    
    # Create a writer object from the csv module
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    
    # Write the header to the CSV file
    writer.writeheader()
    
    # Iterate over the Group dictionary
    for group_key, group_info in Group.items():
        # Extract the group name and policies
        group_name = group_info['name']
        policies = ', '.join(group_info['policies'])  # Join policies into a single string
        
        # Write the group name and policies to the CSV file
        writer.writerow({'GroupName': group_name, 'Policies': policies})

print(f"Group names and policies have been written to {filename}.")
