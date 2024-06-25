import hvac
import csv

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

# Prepare data for CSV
csv_data = []
for group_name, group_info in groups.items():
    # Fetch detailed information about the group to get the associated policies
    group_id = group_info['id']
    group_details = client.secrets.identity.read_group(group_id)
    policies = group_details['data'].get('policies', [])

    csv_data.append([group_name, ', '.join(policies)])

# Define the CSV file path
csv_file = 'vault_groups_policies.csv'

# Write data to CSV
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Group Name', 'Policies'])  # CSV header
    writer.writerows(csv_data)

print(f"Exported group and policy data to {csv_file}")
