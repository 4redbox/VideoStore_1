from flask import Flask, render_template, request, redirect, session
import mysql.connector
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import urllib.parse

app = Flask(__name__)

app.secret_key = 'your_secret_key'  # Set a secret key for session management

# MySQL database configuration
db_config = {
    'host': 'videostore.ce7kmofwez7g.ap-south-1.rds.amazonaws.com',
    'user': 'admin',
    'password': 'password',
    'database': 'vidoes_meta'
}

# Amazon Cognito configuration
COGNITO_REGION = 'ap-south-1'
COGNITO_USER_POOL_ID = 'ap-south-1_fjlNg6c2f'
COGNITO_CLIENT_ID = '5p44v150nnomi197nk75ho0asa'

cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)

# Global variable to store authenticated user token
authenticated_user_token = None

@app.route('/')
def index():
    if 'username' not in session:
        return redirect('/signin')

    # Connect to MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Query to retrieve records from the database
    query = "SELECT id, Name_of_the_class, Day_Recorded, Class_By, Link FROM videos_meta"

    # Check if the username is 'Demo'
    if session.get('username') == 'Demo':
        query += " LIMIT 2"

    cursor.execute(query)
    records = cursor.fetchall()

    # Close the connection
    cursor.close()
    conn.close()

    """
    return render_template('index.html', records=records)

    """

    # Generate signed URLs for the S3 links
    # Explicitly provide the AWS credentials

    aws_access_key_id = 'AKIAZDI6A6DZ34KG7EUD'
    aws_secret_access_key = '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'
    region = 'ap-south-1'

    S3session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    s3_client = S3session.client('s3',region_name=region,config=Config(signature_version='s3v4'))
    signed_records = []
    for record in records:
        s3_url = record[4]  # Assuming the S3 URL is in the fourth column (index 4) of the query result
        parsed_url = urllib.parse.urlparse(s3_url)
        bucket_name = parsed_url.netloc.split(".")[0]
        object_key = urllib.parse.unquote(parsed_url.path[1:])
        try:
            signed_url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket_name,
                    'Key': object_key
                },
                ExpiresIn=3600
            )
            signed_records.append((record[0], record[1], record[2], record[3], signed_url))
        except ClientError as e:
            # Handle any errors that occur during the signing process
            print(f"Error generating signed URL for {s3_url}: {e}")

    # Close the connection
    cursor.close()
    conn.close()

    return render_template('index.html', records=signed_records)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        try:
            response = cognito_client.sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=username,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email}
                ]
            )
            return redirect('/signin')

        except ClientError as e:
            error_message = e.response['Error']['Message']
            return render_template('signup.html', error_message=error_message)

    return render_template('signup.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if 'username' in session:
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            response = cognito_client.initiate_auth(
                ClientId=COGNITO_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )

            session['username'] = username  # Store username in the session
            session['token'] = response['AuthenticationResult']['AccessToken']
            return redirect('/')

        except ClientError as e:
            error_message = e.response['Error']['Message']
            return render_template('signin.html', error_message=error_message)

    return render_template('signin.html')

@app.route('/signout')
def signout():
    session.pop('username', None)  # Remove username from the session
    session.pop('token', None)  # Remove token from the session
    return redirect('/signin')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)