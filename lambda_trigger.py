import pymysql
from datetime import date
import urllib.parse

def lambda_handler(event, context):
    
    try:
        s3_bucket = event['Records'][0]['s3']['bucket']['name']
        s3_object_key = event['Records'][0]['s3']['object']['key']
        aws_region = event['Records'][0]['awsRegion']
        url = f'https://{s3_bucket}.s3.{aws_region}.amazonaws.com/{s3_object_key}'

        s3_values = s3_object_key.split('_')
        batch_id, class_no, class_name, class_by = s3_values[0].split('/')[1], s3_values[1], s3_values[2], s3_values[3].split('.')[0]
        class_name_un = urllib.parse.unquote(class_name).replace('+', ' ')
        date_taken = date.today()
        
        #print(class_no, class_name, batch_id, date_taken, class_by, url)
        
    except KeyError:
        return {
            'statusCode': 400,
            'body': 'Invalid S3 event. Make sure the event structure is correct.'
        }

    try:
        # Connect to the MySQL database
            db_host='database-1.ce7kmofwez7g.ap-south-1.rds.amazonaws.com'
            db_user='videostorer'
            db_password='StupidHacker!990'
            db_name='video_storer'
        
            connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
            )

            with connection.cursor() as cursor:
            # Your select query
            
                #sql_query = "SELECT * FROM video_storer.videos_meta_test; Run this query for testingsss"
                sql_query = f"INSERT INTO videos_meta_test (class_no, class_name,batch_id, date_taken, class_by, url) VALUES ('{class_no}', '{class_name_un}', '{batch_id}', '{date_taken}','{class_by}', '{url}');"
                
                # Execute the query
                cursor.execute(sql_query)
                
                connection.commit()
                
                    
                # Close the database connection
            connection.close()
        
            return {
            'statusCode': 200,
            'body': 'Query executed successfully.'
            }

    except Exception as e:
            return {
            'statusCode': 500,
            'body': str(e)
            }