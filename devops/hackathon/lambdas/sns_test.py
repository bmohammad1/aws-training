import boto3

# Initialize SNS client
sns = boto3.client('sns', region_name='ap-south-1')

# Your SNS Topic ARN
topic_arn = 'arn:aws:sns:ap-south-1:992914516109:evoke-hackathon-test-topic'

# Publish message
response = sns.publish(
    TopicArn=topic_arn,
    Message='Hello from VS Code!',
    Subject='Test SNS Message'
)

print("Message ID:", response['MessageId'])
