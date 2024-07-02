import hvac
import csv
import os

# Configuration - Replace these with your actual Vault details
VAULT_URL = 'http://127.0.0.1:8200'  # Your Vault server URL
ROLE = 'your-role'                  # Your Vault role that matches the GitLab project
MOUNT_PATH = 'auth/jwt'             # Vault JWT authentication mount path (default or custom)

def authenticate_with_gitlab_jwt(client, jwt, role):
    """Authenticate to Vault using the GitLab JWT and return the client with the token set."""
    try:
        auth_response = client.auth.jwt.login(
            role=role,
            jwt=jwt,
            mount_point=MOUNT_PATH
        )
        client.token = auth_response['auth']['client_token']
    except hvac.exceptions.Forbidden:
        print("JWT authentication failed. Please check your JWT and role.")
        exit(1)
    except hvac.exceptions.InvalidRequest as e:
        print(f"JWT authentication error: {e}")
        exit(1)
    
    # Check if the client is authenticated
    if not client.is_authenticated():
        print("Authentication failed. Please check your JWT and Vault configuration.")
        exit(1)
    return client

def retrieve_groups(client):
    """Retrieve the list of groups from Vault."""
    try:
        response = client.secrets.identity.list_groups()
        return response['data']['key_info']
    except hvac.exceptions.InvalidPath:
        print("Failed to retrieve groups. Make sure your Vault setup and path are correct.")
        exit(1)

def write_to_csv(groups, filename='group_policies.csv'):
    """Write the group names and policies to a CSV file."""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['GroupName', 'Policies']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for group_key, group_info in groups.items():
            group_name = group_info['name']
            policies = ', '.join(group_info['policies'])  # Join policies into a single string
            writer.writerow({'GroupName': group_name, 'Policies': policies})

    print(f"Group names and policies have been written to {filename}.")

def main():
    # Initialize the Vault client
    client = hvac.Client(url=VAULT_URL)
    
    # Retrieve the JWT from environment variables or configuration
    gitlab_jwt = os.getenv('CI_JOB_JWT')  # Adjust this if your JWT is stored elsewhere

    if not gitlab_jwt:
        print("JWT not found. Make sure the GitLab JWT is available in the environment variables.")
        exit(1)
    
    # Authenticate the client using GitLab JWT
    client = authenticate_with_gitlab_jwt(client, gitlab_jwt, ROLE)
    
    # Retrieve the list of groups
    groups = retrieve_groups(client)
    
    # Check if the groups list is empty
    if not groups:
        print("No groups found.")
        exit(0)
    
    # Write the groups to CSV
    write_to_csv(groups)

if __name__ == '__main__':
    main()
