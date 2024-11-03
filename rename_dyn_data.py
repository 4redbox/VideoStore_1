import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = 'videos_meta'  # Replace with your DynamoDB table name
table = dynamodb.Table(table_name)

# Old and new URL patterns
old_url_base = "https://cloudtechvideoserver-001a.s3.ap-south-1.amazonaws.com/Test-1/"
new_url_base = "https://videostore-bgtech-server-01.s3.ap-south-1.amazonaws.com/main-video/"

# Scan all records in the table
response = table.scan(Limit=10)
items = response['Items']

# Loop through each item to find and replace the URL
for item in items:
    updated = False
    
    # Check each attribute in the item for the old URL
    for key, value in item.items():
        if isinstance(value, str) and old_url_base in value:
            # Replace the base URL
            new_value = value.replace(old_url_base, new_url_base)
            
            # Replace spaces with "+" in the filename
            new_value = new_value.replace(" ", "+")
            
            # Update the item attribute
            item[key] = new_value
            updated = True
    
    # If there was an update, write it back to the table
    if updated:
        # Update the item back to the table
        table.put_item(Item=item)

print("All records updated successfully.")