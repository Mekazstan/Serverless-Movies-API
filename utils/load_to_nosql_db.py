import boto3
import json
import time
from decouple import config
from botocore.exceptions import ClientError

access_key_id = config("AWS_ACCESS_KEY_ID", default=None)
secret_access_key = config("AWS_SECRET_ACCESS_KEY", default=None)
region_name = config("AWS_DEFAULT_REGION", default=None)

# Initialize a session using Amazon DynamoDB
session = boto3.Session(
    aws_access_key_id= access_key_id,
    aws_secret_access_key= secret_access_key,
    region_name= region_name
)

# Initialize DynamoDB resource
dynamodb = session.resource('dynamodb')

# Function to create a table
def create_movies_table():
    try:
        table = dynamodb.create_table(
            TableName='movies_db',
            KeySchema=[
                {
                    'AttributeName': 'title',
                    'KeyType': 'HASH'  # Partition key
                },
                {
                    'AttributeName': 'releaseYear',
                    'KeyType': 'RANGE'  # Sort key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'title',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'releaseYear',
                    'AttributeType': 'N'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("Table status:", table.table_status)
        table.meta.client.get_waiter('table_exists').wait(TableName='movies_db')
        print("Table is created successfully.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceInUseException':
            print("Table already exists.")
        else:
            print("Unexpected error:", e)

# Function to load data into the table
def load_data(json_file):
    table = dynamodb.Table('movies_db')

    with open(json_file) as f:
        movies = json.load(f)

    for movie in movies:
        table.put_item(Item=movie)
        time.sleep(0.1)  # Sleep to avoid provisioned throughput exceptions

    print("Data has been loaded successfully.")

# Main function
def main():
    create_movies_table()
    load_data('movies_data.json')

if __name__ == '__main__':
    main()
