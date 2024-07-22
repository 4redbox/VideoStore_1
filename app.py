from flask import Flask, render_template, request, redirect, session, jsonify
#import mysql.connector
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config
import urllib.parse
import json
from flask_sslify import SSLify
from loguru import logger

app = Flask(__name__)
sslify = SSLify(app)
region = 'ap-south-1'
logger.add("app.log", rotation="10 MB")
s3_signed_url = ''
print ("s3_signed_url: ",s3_signed_url, flush=True)

def get_aws_secret():

    secret_name = "aws_secrets"
    region_name = region

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    
    # Decrypts secret using the associated KMS key.
    secret1 = get_secret_value_response['SecretString']
    return secret1

def get_aws_secret_2():

    secret_name = "aws_secrets_pool"
    region_name = region

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    
    # Decrypts secret using the associated KMS key.
    secret3 = get_secret_value_response['SecretString']
    return secret3


def select_records_from_dynamodb(query_expression):
    try:
        response = dynamodb.execute_statement(
            Statement=query_expression
        )
        items = response.get('Items', [])
        return items
    except Exception as e:
        print("Error selecting records:", e)
        return []

secret_aws_credentials = get_aws_secret()
aws_credentials = json.loads(secret_aws_credentials)
aws_access = aws_credentials['aws_access_key_id']
aws_secret = aws_credentials['aws_secret_access_key']
pool_id = aws_credentials['COGNITO_USER_POOL_ID']
client_id = aws_credentials['COGNITO_CLIENT_ID']

# Initialize DynamoDB resource

dynamodb = boto3.client('dynamodb', region_name='ap-south-1')

table_name = 'reg_table'
regtable = dynamodb.Table(table_name)

# Amazon Cognito configuration
COGNITO_USER_POOL_ID = pool_id
COGNITO_CLIENT_ID = client_id
print("pool_id_1: ", pool_id)

cognito_client = boto3.client('cognito-idp', region_name=region)
print('cognito_client: ', cognito_client)

"""
secret_aws_credentials_2 = get_aws_secret_2()
aws_credentials_2 = json.loads(secret_aws_credentials_2)
pool_id_2 = aws_credentials_2['COGNITO_USER_POOL_ID']
client_id_2 = aws_credentials_2['COGNITO_CLIENT_ID']

# Amazon Cognito configuration
COGNITO_USER_POOL_ID = pool_id_2
COGNITO_CLIENT_ID = client_id_2

print("pool_id_2: ", pool_id_2)
cognito_client_2 = boto3.client('cognito-idp', region_name=region)
print('cognito_client_2: ', cognito_client_2)
"""

# Global variable to store authenticated user token
authenticated_user_token = None

# Set a secret key for session management
app.secret_key = 'your_secret_key'

def get_rds_secret():

    secret_name = "videos-meta-db"
    region_name = "ap-south-1"

    # Create a Secrets Manager client
    session = boto3.Session(
        aws_access_key_id=aws_access,
        aws_secret_access_key=aws_secret
    )
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e
    
    # Decrypts secret using the associated KMS key.
    secret2 = get_secret_value_response['SecretString']
    return secret2




@app.route('/')

def index():
  
    """
    ##### Code to display user's IP Address ######
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        client_ip = request.environ['REMOTE_ADDR']
    else:
        client_ip = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    if session.get('username') != None:
        logger.info("User " + str(session.get('username')) + " is accessing from: " + str(client_ip))
    """

    if 'username' not in session:
        return redirect('/signin')

    # Connect to MySQL database
    """
    secret_credentials = get_rds_secret()
    credentials = json.loads(secret_credentials)
    rds_host = credentials['host']
    database_name = credentials['database']
    rds_username = credentials['username']
    rds_password = credentials['password']

    conn = mysql.connector.connect(
        host=rds_host,
        port=3306,
        user=rds_username,
        password=rds_password,
        database=database_name
    )    
    cursor = conn.cursor()
    # Query to retrieve records from the database
    batchquery = "SELECT b.Batch_Name,b.Batch_id FROM students a,batch b WHERE a.Batch_id = b.Batch_id and a.Sutdent_User_Name = %s"
    cursor.execute(batchquery, (studentname,))
    batchdetails = cursor.fetchall()
    #print("batchdetails: ",batchdetails)

    if batchdetails:

        for batchdetail in batchdetails:
            batchname = batchdetail[0]
            batchid   = batchdetail[1]
    else:
            batchname = ''
            batchid   = ''

    payment_query = "SELECT Course_Payment FROM students WHERE Sutdent_User_Name = %s"
    cursor.execute(payment_query, (studentname,))
    payment_details = cursor.fetchone()
    if payment_details:
        course_payment = payment_details[0]
    else:
        course_payment = 'No'

    classesquery = "SELECT class_no, class_name, date_taken, class_By, url FROM videos_meta where Batch_id = %s"

    # Check if the payment course is 'No' and print only 4 videos
    if course_payment == 'No':
        classesquery += " LIMIT 4"
    cursor.execute(classesquery, (batchid,))
    records = cursor.fetchall()
    #print("records: ",records)
    
    # Close the connection
    cursor.close()
    conn.close()
    """

    studentname = session.get('username')
    print("before first query")
    print("studentname: ", studentname)

    batch_query = f"SELECT Batch_Name, Batch_id, Course_Payment FROM students WHERE Student_User_Name = ?"

    batch_query_params = [
        {"S": studentname}
    ]

    batchdetails = dynamodb.execute_statement(
        Statement=batch_query,
        Parameters=batch_query_params
    )

    batch_items = batchdetails.get('Items', [])
    batchname = ''
    items = []
    course_payment = 'No'

    if batchdetails:

        for item in batch_items:
            batchname = item['Batch_Name']['S']
            batchid = item['Batch_id']['S']
            course_payment = item['Course_Payment']['S']
    
            print("Batch Name:", batchname)
            print("Batch ID:", batchid)
            print("Payment Course:", course_payment)

            query = f"SELECT session_no, class_name, batch_id, date_taken, class_by, url FROM videos_meta where batch_id = ?"

            batch_query_params_b = [
            {"S": batchid}
            ]

            tabledetails = dynamodb.execute_statement(
            Statement=query,
            Parameters=batch_query_params_b
            )

            items = tabledetails.get('Items', [])

    else:
            batchname = ''
            batchid   = ''
            items = []

    sorted_items_lambda = sorted(items, key=lambda x: int(x['session_no']['S']), reverse=False)

    if course_payment == 'No':
        sorted_items = sorted_items_lambda[:4]
    else:
        sorted_items = sorted_items_lambda

    # Generate signed URLs for the S3 links
   
    S3session = boto3.Session(
        aws_access_key_id=aws_access,
        aws_secret_access_key=aws_secret
    )

    s3_client = S3session.client('s3',region_name=region,config=Config(signature_version='s3v4'))
    signed_records = []
    for item in sorted_items:
        s3_url = item['url']['S']  # Assuming the S3 URL is in the fourth column (index 4) of the query result
        
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
            print("signed_url: ",signed_url,flush=True)
            signed_records.append((item['session_no']['S'], item['class_name']['S'], item['date_taken']['S'], item['class_by']['S'], signed_url))
        except ClientError as e:
            # Handle any errors that occur during the signing process
            print(f"Here Error generating signed URL for {s3_url}: {e}")

    # Close the connection
    #cursor.close()
    #conn.close()

    return render_template('index.html', batchname=batchname, records=signed_records)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
   
        print('cognito_client: ', cognito_client)

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

@app.route('/registration')
def registration():
    return render_template('register.html')  # Ensure 'index.html' matches the HTML file name

@app.route('/register', methods=['POST'])

def register():
    data = request.get_json()
    name = data.get('name')
    Phone = data.get('Phone')
    email = data.get('email')
    experience = data.get('experience')

    # Register the user
    regtable.put_item(Item={
            'name': name,
            'Phone': Phone,
            'email': email,
            'experience': experience
    })
    
    return jsonify({'message': 'Thanks for registering'}), 200

@app.route('/trainersignup', methods=['GET', 'POST'])
def trainersignup():
    if 'username' in session:
        return redirect('/trainer_page_2')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        print('cognito_client: ', cognito_client)
        
        try:
            response = cognito_client.sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=username,
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email}
                ]
            )
            return redirect('/trainer_page_1')

        except ClientError as e:
            error_message = e.response['Error']['Message']
            return render_template('signup.html', error_message=error_message)

    return render_template('trainer_signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if 'username' in session:
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print('In Signin cognito_client: ', cognito_client)

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

@app.route('/trainer_page_1', methods=['GET', 'POST'])
def trainerpage1():

    if 'username' in session and session['username'].startswith('owner'):
        return redirect('/trainer_page_2')
    elif 'username' in session:
        return redirect('/')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        print('cognito_client: ', cognito_client)

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
            print('username in train ', username)
            session['token'] = response['AuthenticationResult']['AccessToken']
           
            if session['username'].startswith('owner'):
                return redirect('/trainer_page_2')
            else:
                return redirect('/')

        except ClientError as e:
            error_message = e.response['Error']['Message']
            return render_template('trainer_page_1.html', error_message=error_message)

    return render_template('trainer_page_1.html')

@app.route('/trainer_page_2')
def trainerpage2():

    student_name_tr = request.args.get('student_name1')

    batch_name_tr = request.args.get('batch_name1')
    print("Received Student Name:", student_name_tr)
    print("Received Batch Name:", batch_name_tr)

    return render_template('trainer_page_2.html')

@app.route('/trainersignout')
def trainersignout():
    session.pop('username', None)  # Remove username from the session
    session.pop('token', None)  # Remove token from the session
    return redirect('/trainer_page_1')

@app.route('/blog')
def blog():
    return render_template("blog.html")

@app.route('/Building-a-Two-Way-Data-Sync')
def blog_post_1():
    return render_template("/blog_posts/Building_a_Two_Way_Data_Sync.html")

@app.route('/signout')
def signout():
    session.pop('username', None)  # Remove username from the session
    session.pop('token', None)  # Remove token from the session
    return redirect('/signin')

@app.route('/video_page', methods=['GET'])
def video_page():
    if request.method == 'GET':
        s3_url = request.args.get('url')
        print("s3_url: ",s3_url, flush=True)
        classname = request.args.get('classname')
        uname = session['username']        
        return render_template('video_page.html', s3_url=s3_url,classname=classname,uname=uname)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
