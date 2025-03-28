import hvac
import csv

# Vault Configuration
VAULT_ADDR = "https://your-vault-instance:8200"
VAULT_TOKEN = "your-vault-token"

# Initialize Vault client
client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN)

# Check authentication
if not client.is_authenticated():
    raise Exception("Authentication to Vault failed!")

# List of engines to EXCLUDE (Only KV & KV-V2)
EXCLUDED_ENGINES = ["kv", "kv-v2"]

# Function to fetch all secret engines dynamically (excluding kv and kv-v2)
def get_secret_engines():
    response = client.sys.list_mounted_secrets_engines()
    return {
        k.rstrip('/'): v['type']
        for k, v in response['data'].items()
        if v['type'] not in EXCLUDED_ENGINES  # Exclude only KV engines
    }

# Function to list secrets dynamically based on engine type
def list_dynamic_secrets(mount_point, engine_type):
    secrets = []
    
    try:
        if engine_type in ["aws", "gcp", "database", "ldap", "rabbitmq"]:
            # Engines that support "roles"
            response = client.secrets.__getattribute__(engine_type).list_roles(mount_point=mount_point)
            secrets = response.get("data", {}).get("keys", [])

        elif engine_type in ["ssh", "database", "ldap"]:
            # Engines that support "users"
            response = client.secrets.__getattribute__(engine_type).list_users(mount_point=mount_point)
            secrets = response.get("data", {}).get("keys", [])

        elif engine_type in ["ad", "iam"]:
            # Engines that support "accounts"
            response = client.secrets.__getattribute__(engine_type).list_accounts(mount_point=mount_point)
            secrets = response.get("data", {}).get("keys", [])

        elif engine_type in ["pki", "transit", "consul"]:
            # Engines that support "keys"
            response = client.secrets.__getattribute__(engine_type).list_keys(mount_point=mount_point)
            secrets = response.get("data", {}).get("keys", [])

        elif engine_type in ["identity"]:
            # Identity secrets engine (uses "entities" and "groups")
            response = client.secrets.identity.list_entities(mount_point=mount_point)
            secrets = response.get("data", {}).get("keys", [])
        
        else:
            return []  # Unsupported secret engine

    except hvac.exceptions.InvalidPath:
        pass  # No secrets found or no permission

    return secrets

# Fetch all secret engines (excluding KV types)
secret_engines = get_secret_engines()

# CSV file to store results
csv_file = "vault_dynamic_secrets.csv"

# Open CSV file for writing
with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Secret Engine Type", "Path", "Secret Count"])

    # Iterate through all discovered secret engines (excluding KV)
    for mount_point, engine_type in secret_engines.items():
        secrets = list_dynamic_secrets(mount_point, engine_type)
        if secrets:  # If secrets exist, it's a dynamic engine
            writer.writerow([engine_type, mount_point, len(secrets)])

print(f"Dynamic secrets data has been written to {csv_file}")
