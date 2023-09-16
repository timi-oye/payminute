import boto3
import psycopg2
import pandas as pd
from sqlalchemy import create_engine
from configparser import ConfigParser

from utils.helper import create_bucket
from utils.constants import db_tables

config = ConfigParser()
config.read('.env')

region = config['AWS']['region']
bucket_name = config['AWS']['bucket_name']
access_key = config['AWS']['access_key']
secret_key = config['AWS']['secret_key']

host = config['DB_CRED']['host']
user = config['DB_CRED']['username']
password = config['DB_CRED']['password']
database = config['DB_CRED']['database']


# Step 1: Create a bucket using boto3
create_bucket(access_key, secret_key, bucket_name)

# Step 2: Extract from Database to Data Lake (S3)

conn = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:5432/{database}')
s3_path = 's3://{}/{}.csv'

for table in db_tables:
    query = f'SELECT * FROM {table}'
    df = pd.read_sql_query(query, conn)

    df.to_csv(
        s3_path.format(bucket_name, table)
        , index=False
        , storage_options={
            'key': access_key
            , 'secret': secret_key
        }
    )