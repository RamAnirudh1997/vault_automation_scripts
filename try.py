# Retrieve the list of groups and their policies
try:
    response = client.secrets.identity.list_groups()
    group_keys = response['data']['keys']  # List of group IDs
    groups = []

    # Fetch details for each group
    for group_id in group_keys:
        group_info = client.secrets.identity.read_group(group_id=group_id)
        group_data = group_info['data']
        group_name = group_data['name']
        policies = ', '.join(group_data['policies'])  # Join policies into a single string
        groups.append({'GroupName': group_name, 'Policies': policies})
except hvac.exceptions.InvalidPath:
    print("Failed to retrieve groups. Make sure your Vault setup and path are correct.")
    exit(1)

# Write the groups and their policies to a CSV file
filename = 'group_policies.csv'
with open(filename, 'w', newline='') as csvfile:
    fieldnames = ['GroupName', 'Policies']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    for group in groups:
        writer.writerow(group)

print(f"Group names and policies have been written to {filename}.")
