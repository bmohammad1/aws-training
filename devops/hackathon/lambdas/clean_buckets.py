import boto3
import os

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    client = boto3.client('s3')
    results = []

    # Get and normalize the env variable ONCE at the top
    excluded = os.getenv('EXCLUDED_BUCKET_NAME')
    if excluded:
        excluded = excluded.strip().lower()  # strip whitespace and lowercase for safe comparison
    else:
        excluded = ""  # fallback -- never matches but don't crash

    for bucket in s3.buckets.all():
        bucket_name = bucket.name
        # Normalize bucket_name for comparison
        bucket_name_norm = bucket_name.strip().lower()
        print(f"Processing bucket: {bucket_name}")
        print(f"Exclude '{excluded}'")
        print(f"repr(bucket_name)={repr(bucket_name)}, repr(excluded)={repr(excluded)}")

        # Skip the excluded bucket
        if bucket_name_norm == excluded:
            print(f"Skipping bucket: {bucket_name} (excluded)")
            continue
    

        # Check if bucket versioning is enabled
        versioning = client.get_bucket_versioning(Bucket=bucket_name)
        is_versioned = versioning.get("Status") == "Enabled"
        deleted = 0

        if is_versioned:
            print(f"Bucket {bucket_name} is versioned. Deleting all versions and delete markers.")
            # Delete all versions (including delete markers)
            paginator = client.get_paginator('list_object_versions')
            for page in paginator.paginate(Bucket=bucket_name):
                versions = page.get('Versions', []) + page.get('DeleteMarkers', [])
                for obj in versions:
                    client.delete_object(
                        Bucket=bucket_name,
                        Key=obj['Key'],
                        VersionId=obj['VersionId']
                    )
                    deleted += 1
        else:
            print(f"Bucket {bucket_name} is not versioned. Deleting all objects.")
            paginator = client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=bucket_name):
                for obj in page.get('Contents', []):
                    client.delete_object(Bucket=bucket_name, Key=obj['Key'])
                    deleted += 1

        msg = f"Emptied bucket: {bucket_name} ({deleted} objects/versions deleted)"
        print(msg)
        results.append(msg)

    return {"results": results}