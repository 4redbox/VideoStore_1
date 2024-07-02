import boto3
import mysql.connector
import datetime


def lambda_handler(event, context):
    # Get the uploaded file details
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    file_name = file_key.split('/')[-1]  # Extract the file name from the key

    # Split the file name by '_'
    file_parts = file_name.split('_')

    # Generate the S3 URL
    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{file_key}"

    today_date = datetime.date.today()

    # Prepare the insert query
    query = "INSERT INTO video_storer.videos_meta class_no, class_name, batch_id, date_taken, class_by, url) VALUES (%s, %s, %s, %s, %s, %s);"

    values = (file_parts[0], file_parts[1], file_parts[2], today_date,file_parts[3], s3_url)

    # Execute the insert query
    conn = mysql.connector.connect(
        'host': 'database-1.ce7kmofwez7g.ap-south-1.rds.amazonaws.com',
        'user': 'videostorer',
        'password': 'StupidHacker!990',
        'database': 'video_storer'
    )

    cursor = conn.cursor()
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

    # Optionally, print the query for debugging purposes
    print("Insert query executed:", query)