# CreatePresignedURLS3Object
A presigned URL is generated every time an object is put into an specific Amazon S3 bucket. 
The URL is published to a topic via Amazon SNS.
Al generated URLs are stored in an Amazon DynamoDB table.
