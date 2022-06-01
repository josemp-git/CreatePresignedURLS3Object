import boto3
import datetime
from datetime import datetime
import time

def lambda_handler(event, context):
    s3Client = boto3.client("s3")
    snsClient = boto3.client("sns")
    dynamodb = boto3.resource('dynamodb')
    
    #Time in seconds for the presigned URL to expire
    #2628000 seconds = 730 hours = 1 month
    expiryTime = "2628000"

    #SNS Topic to publish the URL.
    topic_arn = "arn:aws:sns:*REGION*:*ACCOUNT*:*TOPIC*"
    
    #Object and bucket names are taken from the PUT
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_name = event['Records'][0]['s3']['object']['key']
    
    #Presigned URL is generated
    url = s3Client.generate_presigned_url('get_object',
        Params = {'Bucket': bucket_name, 'Key': object_name},
        ExpiresIn = expiryTime
        )
    #print("Esta es la url: " + url)
    print(object_name)
    
        #Generated URLs are saved in a DynamoDB table
    table = dynamodb.Table('S3_Objects_Presigned_URLs') 
    
    #Creation and expiration dates are inserted in the DynamoDB table
    now = datetime.now()
    creation_time = now.strftime('%Y-%m-%d, %H:%M:%S')
    expiration_time_epoch = int(url[-10:])
    expiration_time = time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime(expiration_time_epoch))
    
    #S3 object URI is also inserted in the DynamoDB table
    s3_uri = 's3://' + bucket_name + '/' + object_name
    
    #put_item
    table.put_item(Item={
            'Object_name': object_name,
            'Creation_time': creation_time,
            'Expiration_time': expiration_time,
            'URL': url,
            'S3_URI': s3_uri
        })
    
    #Email parameters. ;essage is sent with file name (S3 object), URL and expiration date.
    mail_message = "File: " + object_name + ". Expires: " + expiration_time + " (UTC). URL: " + url
    mail_subject = "URL ready"
    snsClient.publish(
        TopicArn=topic_arn,
        Message=mail_message,
        Subject=mail_subject,
        )