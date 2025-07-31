import hvac
import csv
#I want to test git
# Vault Configuration
VAULT_ADDR = "https://your-vault-instance:8200"
try there
VAULT_TOKEN = "your-vault-token"
NAMESPACE = "admin"  # Namespace to pass

# Initialize Vault client with namespace
client = hvac.Client(url=VAULT_ADDR, token=VAULT_TOKEN, namespace=NAMESPACE)

# Check authentication
if not client.is_authenticated():
    raise Exception("Authentication to Vault failed!")

# Function to fetch all **dynamic** secret engines (excluding KV)
def get_dynamic_secret_engines():
    response = client.sys.list_mounted_secrets_engines()
    return {
        mount_point.rstrip('/'): details['type']
        for mount_point, details in response['data'].items()
        if details['type'] not in ["kv", "kv-v2"]  # Exclude KV engines
    }

# Function to list AWS roles
def list_aws_roles(mount_point):
    try:
        response = client.secrets.aws.list_roles(mount_point=mount_point)
        return response.get("data", {}).get("keys", [])
    except hvac.exceptions.InvalidPath:
        return []

# Function to list GCP static accounts
def list_gcp_accounts(mount_point):
    try:
        response = client.secrets.gcp.list_roles(mount_point=mount_point)
        return response.get("data", {}).get("keys", [])
    except hvac.exceptions.InvalidPath:
        return []

# Function to list Database roles (static and dynamic)
def list_db_roles(mount_point):
    db_roles = []
    try:
        # List dynamic database roles
        response = client.secrets.database.list_roles(mount_point=mount_point)
        db_roles.extend(response.get("data", {}).get("keys", []))

        # If there are static roles, they can be handled here as well (same path as dynamic)
        # This depends on your Vault setup for static roles handling
        # You can extend this logic if there's another path for static roles (if applicable)

    except hvac.exceptions.InvalidPath:
        print(f"⚠️ No Database roles found or access denied for: {mount_point}")
    return db_roles

# Function to list LDAP static roles
def list_ldap_roles(mount_point):
    try:
        response = client.secrets.ldap.list_roles(mount_point=mount_point)
        return response.get("data", {}).get("keys", [])
    except hvac.exceptions.InvalidPath:
        return []

# Fetch all dynamic secret engines
dynamic_secret_engines = get_dynamic_secret_engines()

# CSV file to store results
csv_file = "vault_dynamic_secrets.csv"

# Open CSV file for writing
with open(csv_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Namespace", "Secrets Mount", "Secrets Path", "Key Count"])

    # Iterate through secret engines and collect data
    for mount_point, engine_type in dynamic_secret_engines.items():
        if engine_type == "aws":
            aws_roles = list_aws_roles(mount_point)
            writer.writerow([NAMESPACE, mount_point, f"{mount_point}/roles", len(aws_roles)])

        elif engine_type == "gcp":
            gcp_accounts = list_gcp_accounts(mount_point)
            writer.writerow([NAMESPACE, mount_point, f"{mount_point}/roles", len(gcp_accounts)])

        elif engine_type == "database":
            db_roles = list_db_roles(mount_point)
            writer.writerow([NAMESPACE, mount_point, f"{mount_point}/roles", len(db_roles)])

        elif engine_type == "ldap":
            ldap_roles = list_ldap_roles(mount_point)
            writer.writerow([NAMESPACE, mount_point, f"{mount_point}/roles", len(ldap_roles)])

print(f"✅ Secrets data has been written to {csv_file}")

