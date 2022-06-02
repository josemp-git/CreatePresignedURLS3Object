 import boto3
 import datetime
 from datetime import datetime
 import time
 import os
 
 def lambda_handler(event, context):
     s3Client = boto3.client("s3")
     snsClient = boto3.client("sns")
     dynamodb = boto3.resource('dynamodb')
     
     #Time in seconds for the presigned URL to expire
     #Example: 2628000 seconds = 730 hours = 1 month
     expiryTime = os.environ['url_expiration_time']
     
     #Object and bucket names are taken from the PUT
     bucket_name = event['Records'][0]['s3']['bucket']['name']
     object_name = event['Records'][0]['s3']['object']['key']
     
     #Presigned URL is generated
     url = s3Client.generate_presigned_url('get_object',
         Params = {'Bucket': bucket_name, 'Key': object_name},
         ExpiresIn = expiryTime
         )
     
     #Creation and expiration time of the presigned URLs
     now = datetime.now()
     creation_time = now.strftime('%Y-%m-%d, %H:%M:%S')
     expiration_time_epoch = int(url[-10:])
     expiration_time = time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime(expiration_time_epoch))
     
     #S3 object URI
     s3_uri = 's3://' + bucket_name + '/' + object_name
     
     #Generated URLs are saved in a DynamoDB table along with the S3 object URI and creation/expiration time
     table = dynamodb.Table('S3_Objects_Presigned_URLs') 
     table.put_item(Item={
             'Object_name': object_name,
             'Creation_time': creation_time,
             'Expiration_time': expiration_time,
             'URL': url,
             'S3_URI': s3_uri
         })
     
     #SNS Topic to publish the URL.
     topic_arn = os.environ['topic_arn']
     
     #Email parameters. Email message is sent via SNS with file name (S3 object), URL and expiration date.
     mail_message = "File: " + object_name + ". Expires: " + expiration_time + " (UTC). URL: " + url
     mail_subject = "URL ready"
     snsClient.publish(
         TopicArn=topic_arn,
         Message=mail_message,
         Subject=mail_subject,
         )