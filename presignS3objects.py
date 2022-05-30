import boto3

def lambda_handler(event, context):
    s3Client = boto3.client("s3")
    snsClient = boto3.client("sns")
    
    #¿Cuantos segundos dura disponible la liga?
    #2628000 segundos = 730 horas = 1 mes
    expiryTime = "2628000"
    
    #SNS Topic al cuál se va a mandar la liga de descarga, se ingresa el ARN del tópíco.
    topic_arn ="arn:aws:sns:*REGION*:*ACCOUNT*:*TOPIC*"
    
    #Nombres del objeto y del bucket se toman del evento PUT
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_name = event['Records'][0]['s3']['object']['key']
    
    #Se firma el objeto
    url = s3Client.generate_presigned_url('get_object',
        Params = {'Bucket': bucket_name, 'Key': object_name},
        ExpiresIn = expiryTime
        )
    #print("Esta es la url: " + url)
    
    #Se manda el correo
    mail_message = "Esta es la url del reporte: " + url
    mail_subject = "Reporte listo"
    mandar_correo = snsClient.publish(
        TopicArn=topic_arn,
        Message=mail_message,
        Subject=mail_subject,
        )
