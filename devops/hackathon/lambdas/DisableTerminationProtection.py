import boto3

def lambda_handler(event, context):
    region = 'ap-south-1' 
    ec2 = boto3.client('ec2', region_name=region)

    paginator = ec2.get_paginator('describe_instances')
    all_instance_ids = []
    for page in paginator.paginate():
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:
                all_instance_ids.append(instance['InstanceId'])

    results = []

    for instance_id in all_instance_ids:
        # Get the current disableApiTermination attribute
        attr = ec2.describe_instance_attribute(
            InstanceId=instance_id,
            Attribute='disableApiTermination'
        )
        val = attr['DisableApiTermination']['Value']
        if val:
            # Disable termination protection
            ec2.modify_instance_attribute(
                InstanceId=instance_id,
                DisableApiTermination={'Value': False}
            )
            msg = f"Disabled termination protection for instance {instance_id}"
        else:
            msg = f"Termination protection already off for {instance_id}"
        print(msg)
        results.append(msg)

    return {
        "message": f"Processed {len(all_instance_ids)} EC2 instances.",
        "details": results
    }