import boto3
import csv

# Initialize the DynamoDB client
dynamodb = boto3.client('dynamodb')

# Define the name of your DynamoDB table
table_name = 'videos_meta'

# Define the path to your CSV file
csv_file_path = r'C:\Users\raja4\Documents\org_selected.csv'

# Function to read CSV and upload records to DynamoDB
def upload_csv_to_dynamodb():
    with open(csv_file_path, 'r', newline='') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        batch_size = 18  # Adjust the batch size as needed

        # Initialize an empty batch of DynamoDB write requests
        batch_requests = []

        # Iterate over each row in the CSV
        for row in csv_reader:
            # Transform the CSV row into DynamoDB item format
            item = {
                'class_no': {'S': row['class_no']},
                'batch_id': {'S': row['batch_id']},
                'class_by': {'S': row['class_by']},
                'class_name': {'S': row['class_name']},
                'date_taken': {'S': row['date_taken']},
                'session_no': {'S': row['session_no']},
                'url': {'S': row['url']},
                # Add more attributes as needed
            }

            # Add the item to the batch write request
            batch_requests.append({
                'PutRequest': {
                    'Item': item
                }
            })

            # If the batch size reaches the specified limit, execute the batch write operation
            if len(batch_requests) >= batch_size:
                execute_batch_write(batch_requests)
                batch_requests = []

        # Execute the final batch write operation
        if batch_requests:
            execute_batch_write(batch_requests)

# Function to execute batch write operation
def execute_batch_write(batch_requests):
    response = dynamodb.batch_write_item(
        RequestItems={
            table_name: batch_requests
        }
    )
    print("Batch write response:", response)

# Call the function to upload CSV records to DynamoDB
upload_csv_to_dynamodb()
