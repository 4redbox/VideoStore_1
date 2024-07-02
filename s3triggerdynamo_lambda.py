import boto3
from datetime import date
import urllib.parse
    
def get_max_class_no(dynamodb, table_name):
       
        response = dynamodb.scan(
            TableName=table_name,
            Select="ALL_ATTRIBUTES"
        )
        
        class_no_values = []
        
        for item in response['Items']:
            if 'class_no' in item and 'S' in item['class_no']:
                class_no_values.append(int(item['class_no']['S']))
        
        max_class_no = max(class_no_values)
        
        return max_class_no
        

def lambda_handler(event, context):
    try:
        s3_bucket = event['Records'][0]['s3']['bucket']['name']
        s3_object_key = event['Records'][0]['s3']['object']['key']
        aws_region = event['Records'][0]['awsRegion']
        url = f'https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{s3_object_key}'
        
        s3_values = s3_object_key.split('_')
        batch_id, session_no, class_name, class_by = s3_values[0].split('/')[1], s3_values[1], s3_values[2], s3_values[3].split('.')[0]
        class_name_un = urllib.parse.unquote(class_name).replace('+', ' ')
        class_no = '099'
        date_taken = str(date.today())
        
    except KeyError:
        return {
            'statusCode': 400,
            'body': 'Invalid S3 event. Make sure the event structure is correct.'
        }

    try:
        # Create a DynamoDB client
        dynamodb = boto3.client('dynamodb', region_name='ap-south-1')
        
        # Define the DynamoDB table name
        table_name = 'videos_meta'  # Change to your DynamoDB table name
        
        # Fetch the current maximum class_no and increment it by 1
        max_class_no = get_max_class_no(dynamodb, table_name) + 1
        print('Max Class:', max_class_no)
        class_no = max_class_no
        
        # Check if the session_no already exists for the batch_id
        #if session_exists(dynamodb, table_name, batch_id, session_no):
        #    return {
        #        'statusCode': 400,
        #        'body': 'Session number already exists for the batch.'
        #    }
        
        # Prepare the item to be inserted
        item = {
            'class_no': {'S': str(class_no)},
            'session_no': {'S': session_no},
            'class_name': {'S': class_name_un},
            'batch_id': {'S': batch_id},
            'date_taken': {'S': date_taken},
            'class_by': {'S': class_by},
            'url': {'S': url}
        }
        
        # Insert the item into DynamoDB
        dynamodb.put_item(
            TableName=table_name,
            Item=item
        )
        
        return {
            'statusCode': 200,
            'body': 'Item inserted successfully into DynamoDB.'
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }