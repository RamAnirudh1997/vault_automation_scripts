import os
import hvac
import getpass

# Configuration from environment variables
vault_url = os.getenv('VAULT_URL')
vault_role = os.getenv('VAULT_ROLE')
vault_secret_path = os.getenv('VAULT_SECRET_PATH')
gitlab_jwt = os.getenv('CI_JOB_JWT')  # GitLab provides the JWT token automatically in CI

# Ensure necessary environment variables are set
if not all([vault_url, vault_role, vault_secret_path, gitlab_jwt]):
    print("Missing required environment variables. Please check VAULT_URL, VAULT_ROLE, VAULT_SECRET_PATH, and CI_JOB_JWT.")
    exit(1)

# Initialize the Vault client
client = hvac.Client(url=vault_url)

# Authenticate with GitLab JWT
try:
    auth_response = client.auth.gitlab.login(
        role=vault_role,
        jwt=gitlab_jwt
    )
    client.token = auth_response['auth']['client_token']
except hvac.exceptions.Forbidden:
    print("GitLab authentication failed. Please check your role and JWT token.")
    exit(1)
except hvac.exceptions.InvalidRequest as e:
    print(f"GitLab authentication error: {e}")
    exit(1)

# Check if the client is authenticated
if not client.is_authenticated():
    print("Authentication failed. Please check your GitLab credentials.")
    exit(1)

# Prompt for secrets securely
try:
    secret_key = getpass.getpass(prompt='Enter the secret key: ')
    secret_value = getpass.getpass(prompt='Enter the secret value: ')
except Exception as error:
    print(f"Error retrieving input: {error}")
    exit(1)

# Onboard secret to Vault
try:
    client.secrets.kv.v2.create_or_update_secret(
        path=vault_secret_path,
        secret={secret_key: secret_value}
    )
    print(f"Secret for key '{secret_key}' successfully stored in path '{vault_secret_path}'.")
except Exception as error:
    print(f"Error storing secret: {error}")
    exit(1)

# Return the Vault token (optional)
print(client.token)
