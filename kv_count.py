import os
import requests

# Ensure VAULT_ADDR and VAULT_TOKEN are set
VAULT_ADDR = os.getenv("VAULT_ADDR", "https://your-vault-address")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "your-vault-token")

# Define the kv-v2 secrets engine path
KV_PATH = "kv-v2"  # Adjust this to your actual kv-v2 path

# Function to list all secrets recursively
def list_secrets(path):
    url = f"{VAULT_ADDR}/v1/{KV_PATH}/metadata/{path}"
    headers = {
        "X-Vault-Token": VAULT_TOKEN
    }
    response = requests.request("LIST", url, headers=headers)
    response.raise_for_status()
    return response.json().get('data', {}).get('keys', [])

# Recursive function to count secrets
def count_secrets(path=""):
    count = 0
    secrets = list_secrets(path)
    for secret in secrets:
        if secret.endswith('/'):
            count += count_secrets(f"{path}{secret}")
        else:
            count += 1
    return count

try:
    total_secrets = count_secrets()
    print(f"Total number of secrets: {total_secrets}")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")

import os
import hvac

# Ensure VAULT_ADDR and VAULT_TOKEN are set
VAULT_ADDR = os.getenv("VAULT_ADDR", "https://your-vault-address")
VAULT_TOKEN = os.getenv("VAULT_TOKEN", "your-vault-token")

# Initialize the hvac client
client = hvac.Client(
    url=VAULT_ADDR,
    token=VAULT_TOKEN,
)

# Define the kv-v2 secrets engine path
KV_PATH = "kv-v2"  # Adjust this to your actual kv-v2 path

# Function to list all secrets recursively
def list_secrets(path):
    response = client.secrets.kv.v2.list_secrets(
        mount_point=KV_PATH,
        path=path
    )
    return response['data']['keys']

# Recursive function to count secrets
def count_secrets(path=""):
    count = 0
    secrets = list_secrets(path)
    for secret in secrets:
        if secret.endswith('/'):
            count += count_secrets(f"{path}{secret}")
        else:
            count += 1
    return count

try:
    total_secrets = count_secrets()
    print(f"Total number of secrets: {total_secrets}")
except hvac.exceptions.VaultError as e:
    print(f"Error: {e}")


