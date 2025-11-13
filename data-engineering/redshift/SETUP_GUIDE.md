# Setup Guide - S3 to Redshift Data Pipeline# 🔧 REQUIRED CHANGES TO MAKE AUTOMATION WORK

This comprehensive guide will walk you through setting up the automated S3 to Redshift data pipeline from scratch.## ⚡ QUICK START GUIDE

## 📋 Prerequisites Checklist### **Step 1: Initial Setup**

Before starting, ensure you have:```powershell

cd data-engineering\redshift\scripts

- [ ] **AWS Account** with administrator or sufficient permissionspython setup.py

- [ ] **Python 3.9 or higher** installed on your local machine```

- [ ] **AWS CLI** installed and configured

- [ ] **Git** for version controlThis will:

- [ ] **Amazon Redshift cluster** provisioned and accessible

- [ ] **S3 bucket** created for data storage- ✅ Verify AWS credentials

- ✅ Check Redshift workgroup exists

## 🔧 Environment Setup- ✅ Generate SQL setup commands

- ✅ Prompt for your email address

### 1. Local Development Environment

### **Step 2: Create Redshift Tables**

#### Install Python Dependencies

Run the generated `redshift_setup.sql` in your Redshift Query Editor:

````bash

# Create and activate virtual environment```sql

python -m venv venv-- These tables will be created:

CREATE TABLE orders (order_id, customer_id, order_date, total_amount, status);

# Activate virtual environmentCREATE TABLE orders_staging (same structure for UPSERT);

# On Windows:CREATE TABLE order_items (item_id, order_id, product_id, quantity, price);

venv\Scripts\activateCREATE TABLE order_items_staging (same structure for UPSERT);

# On Linux/Mac:```

source venv/bin/activate

### **Step 3: Deploy Automation**

# Install required packages

pip install boto3 pandas pyarrow psycopg2-binary faker```powershell

```python deploy.py

````

#### Verify Python Installation

Enter when prompted:

````bash

python --version  # Should be 3.9+- **Email**: Your real email address (for notifications)

pip list | grep -E "(boto3|pandas|pyarrow)"- **Stack name**: Press Enter for default

```- **Region**: Press Enter for default (us-east-1)



### 2. AWS CLI Configuration### **Step 4: Test the Pipeline**



#### Install AWS CLI (if not already installed)```powershell

# Generate test data

```bashpython order_generator.py

# Windows (using pip)python json_to_parquet.py

pip install awscli

# Upload to trigger automation

# macOS (using Homebrew)aws s3 cp ../parquet_files/orders.parquet s3://siddhartha-redshift-bucket/orders/

brew install awscli```



# Linux (using package manager)## 📋 DETAILED REQUIREMENTS

sudo apt-get install awscli  # Ubuntu/Debian

sudo yum install awscli      # RHEL/CentOS### **1. AWS Prerequisites**

````

**AWS CLI configured:**

#### Configure AWS Credentials

````powershell

```bashaws configure list        # Check current config

aws configureaws sts get-caller-identity   # Verify access

````

Enter the following when prompted:**Required IAM permissions:**

- **AWS Access Key ID**: Your access key

- **AWS Secret Access Key**: Your secret key- CloudFormation: Create/update stacks

- **Default region name**: e.g., `us-east-1`- Lambda: Create/update functions

- **Default output format**: `json`- S3: Create buckets and manage objects

- SNS: Create topics and send messages

#### Verify AWS Configuration- Redshift Data API: Execute queries

- IAM: Create roles for services

````bash

# Test AWS connectivity### **2. AWS Account Information Needed**

aws sts get-caller-identity

**These will be automatically detected:**

# List S3 buckets (should not error)

aws s3 ls- ✅ **AWS Account ID**: Auto-detected by CloudFormation

```- ✅ **Region**: Specified in deployment (default: us-east-1)

- ✅ **Email Address**: You provide during deployment

## 🏗️ Infrastructure Setup

### **3. Redshift Configuration**

### 1. Create S3 Bucket

**Existing setup (should already work):**

#### Using AWS CLI

- ✅ **Workgroup**: `order-analytics-workgroup1`

```bash- ✅ **Database**: `dev`

# Create bucket (replace with your unique bucket name)

export BUCKET_NAME="your-unique-bucket-name-$(date +%s)"**New tables needed (create once):**

aws s3 mb s3://$BUCKET_NAME

```sql

# Enable versioning-- Copy these commands to Redshift Query Editor

aws s3api put-bucket-versioning \CREATE TABLE IF NOT EXISTS orders (

    --bucket $BUCKET_NAME \    order_id VARCHAR(50) PRIMARY KEY,

    --versioning-configuration Status=Enabled    customer_id VARCHAR(50),

    order_date TIMESTAMP,

# Enable server-side encryption    total_amount DECIMAL(10,2),

aws s3api put-bucket-encryption \    status VARCHAR(20)

    --bucket $BUCKET_NAME \);

    --server-side-encryption-configuration '{

        "Rules": [CREATE TABLE IF NOT EXISTS orders_staging (

            {    order_id VARCHAR(50),

                "ApplyServerSideEncryptionByDefault": {    customer_id VARCHAR(50),

                    "SSEAlgorithm": "AES256"    order_date TIMESTAMP,

                }    total_amount DECIMAL(10,2),

            }    status VARCHAR(20)

        ]);

    }'```

````

### **4. Code Changes Already Made**

#### Using AWS Console

**✅ Lambda function updated:**

1. Go to [S3 Console](https://console.aws.amazon.com/s3/)

2. Click "Create bucket"- Uses environment variables instead of hardcoded values

3. Enter unique bucket name- Configured for Redshift Serverless (workgroup instead of cluster)

4. Select your region- Proper error handling and notifications

5. Enable "Bucket Versioning"

6. Enable "Default encryption" with SSE-S3**✅ Deployment script updated:**

7. Click "Create bucket"

- Fixed file paths for new folder structure

### 2. Set Up Amazon Redshift- Automatic AWS account detection

- Interactive email configuration

#### Create Redshift Cluster (if needed)

**✅ CloudFormation template ready:**

```````bash

# Create Redshift cluster using AWS CLI- Creates all required AWS resources

aws redshift create-cluster \- Sets proper permissions and triggers

    --cluster-identifier my-redshift-cluster \- Configures S3→Lambda→SNS→Redshift pipeline

    --node-type dc2.large \

    --master-username awsuser \## 🔥 WHAT HAPPENS AFTER DEPLOYMENT

    --master-user-password YourSecurePassword123! \

    --db-name dev \### **AWS Resources Created:**

    --cluster-type single-node \

    --publicly-accessible| Resource            | Name                                    | Purpose                                 |

```| ------------------- | --------------------------------------- | --------------------------------------- |

| **S3 Bucket**       | `siddhartha-redshift-bucket`            | Upload destination with Lambda triggers |

#### Configure Redshift Security Group| **Lambda Function** | `S3RedshiftAutomation`                  | Processes uploads, loads to Redshift    |

| **SNS Topic**       | `redshift-upload-notifications`         | Sends email alerts                      |

```bash| **IAM Roles**       | `LambdaExecutionRole`, `RedshiftS3Role` | Security permissions                    |

# Get your current IP address| **CloudWatch Logs** | `/aws/lambda/S3RedshiftAutomation`      | Monitoring and debugging                |

MY_IP=$(curl -s https://ifconfig.me)

### **Automatic Workflow:**

# Authorize your IP for Redshift access

aws redshift authorize-cluster-security-group-ingress \```

    --cluster-security-group-name default \📁 Upload .parquet to S3

    --cidr-ip $MY_IP/32    ↓

```⚡ Lambda triggered automatically

    ↓

#### Test Redshift Connection📧 Email: "File uploaded by John"

    ↓

```bash🗄️ Redshift COPY to staging table

# Install psql (PostgreSQL client)    ↓

# Ubuntu/Debian:🔄 UPSERT: DELETE duplicates + INSERT new

sudo apt-get install postgresql-client    ↓

✅ Email: "Processing completed successfully"

# macOS:```

brew install postgresql

## 🧪 TESTING THE AUTOMATION

# Test connection (replace with your cluster endpoint)

psql -h your-cluster.xxxxx.us-east-1.redshift.amazonaws.com \### **1. Generate Test Data**

     -U awsuser -d dev -p 5439

``````powershell

cd scripts

### 3. Create IAM Rolespython order_generator.py    # Creates sample orders

python json_to_parquet.py    # Converts to optimized format

#### Lambda Execution Role```



Create `lambda-execution-role.json`:### **2. Upload Test File**



```json```powershell

{# This will trigger the entire pipeline

    "Version": "2012-10-17",aws s3 cp ../parquet_files/orders.parquet s3://siddhartha-redshift-bucket/orders/

    "Statement": [```

        {

            "Effect": "Allow",### **3. Check Results**

            "Principal": {

                "Service": "lambda.amazonaws.com"**Email notifications:**

            },

            "Action": "sts:AssumeRole"- Upload notification with uploader info

        }- Processing completion status

    ]

}**CloudWatch logs:**

```````

```powershell

Create `lambda-execution-policy.json`:aws logs tail /aws/lambda/S3RedshiftAutomation --follow

```

````json

{**Redshift data:**

    "Version": "2012-10-17",

    "Statement": [```sql

        {SELECT COUNT(*) FROM orders;  -- Should show new records

            "Effect": "Allow",SELECT * FROM orders ORDER BY order_date DESC LIMIT 5;

            "Action": [```

                "logs:CreateLogGroup",

                "logs:CreateLogStream",## 🆘 TROUBLESHOOTING

                "logs:PutLogEvents"

            ],### **Common Issues:**

            "Resource": "arn:aws:logs:*:*:*"

        },**1. Email not working:**

        {

            "Effect": "Allow",- Check spam folder

            "Action": [- Confirm SNS subscription in email

                "s3:GetObject",- Verify email address in CloudFormation parameters

                "s3:GetObjectMetadata"

            ],**2. Redshift connection errors:**

            "Resource": "arn:aws:s3:::your-bucket-name/*"

        },- Verify workgroup name: `order-analytics-workgroup1`

        {- Check workgroup status is "available"

            "Effect": "Allow",- Ensure tables exist (run setup SQL)

            "Action": [

                "redshift-data:ExecuteStatement",**3. Lambda permission errors:**

                "redshift-data:DescribeStatement",

                "redshift-data:GetStatementResult"- CloudFormation creates all permissions automatically

            ],- Check stack deployment completed successfully

            "Resource": "*"- Verify IAM roles created: `LambdaExecutionRole`, `RedshiftS3Role`

        },

        {**4. S3 upload not triggering:**

            "Effect": "Allow",

            "Action": [- Upload must be .parquet file

                "sqs:SendMessage"- Check bucket notification configuration

            ],- Verify Lambda function exists and is active

            "Resource": "arn:aws:sqs:*:*:s3-redshift-dlq"

        }### **Debug Commands:**

    ]

}```powershell

```# Check CloudFormation stack

aws cloudformation describe-stacks --stack-name s3-redshift-automation

Create the IAM role:

# Verify Lambda function

```bashaws lambda get-function --function-name S3RedshiftAutomation

# Create the role

aws iam create-role \# Check S3 bucket notifications

    --role-name lambda-s3-redshift-execution-role \aws s3api get-bucket-notification-configuration --bucket siddhartha-redshift-bucket

    --assume-role-policy-document file://lambda-execution-role.json

# View recent logs

# Attach the custom policyaws logs describe-log-streams --log-group-name /aws/lambda/S3RedshiftAutomation

aws iam put-role-policy \```

    --role-name lambda-s3-redshift-execution-role \

    --policy-name lambda-s3-redshift-policy \## ✅ SUCCESS INDICATORS

    --policy-document file://lambda-execution-policy.json

**Deployment successful when:**

# Attach AWS managed policy for Lambda basic execution

aws iam attach-role-policy \- ✅ CloudFormation stack shows "CREATE_COMPLETE"

    --role-name lambda-s3-redshift-execution-role \- ✅ Lambda function visible in AWS Console

    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole- ✅ S3 bucket created with event notifications

```- ✅ SNS subscription confirmation email received

- ✅ Test upload triggers Lambda execution

#### Redshift Service Role- ✅ Data appears in Redshift tables

- ✅ Success notification email received

Create `redshift-service-role.json`:

**Your automation is working when you can:**

```json

{1. Upload a .parquet file to S3

    "Version": "2012-10-17",2. Receive immediate upload notification

    "Statement": [3. See data loaded in Redshift

        {4. Receive processing completion notification

            "Effect": "Allow",

            "Principal": {---

                "Service": "redshift.amazonaws.com"

            },**🎉 Ready to deploy? Start with `python setup.py`!**

            "Action": "sts:AssumeRole"
        }
    ]
}
````

Create `redshift-s3-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["s3:GetObject", "s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

Create the Redshift service role:

```bash
# Create the role
aws iam create-role \
    --role-name redshift-s3-copy-role \
    --assume-role-policy-document file://redshift-service-role.json

# Attach the S3 access policy
aws iam put-role-policy \
    --role-name redshift-s3-copy-role \
    --policy-name redshift-s3-access-policy \
    --policy-document file://redshift-s3-policy.json
```

## 🚀 Lambda Function Deployment

### 1. Package Lambda Function

```bash
# Create deployment package
cd automation/
zip -r ../lambda-deployment-package.zip .

# Verify package contents
zipinfo ../lambda-deployment-package.zip
```

### 2. Create Lambda Function

```bash
# Get the Lambda execution role ARN
LAMBDA_ROLE_ARN=$(aws iam get-role \
    --role-name lambda-s3-redshift-execution-role \
    --query 'Role.Arn' --output text)

# Create Lambda function
aws lambda create-function \
    --function-name s3-redshift-automation \
    --runtime python3.9 \
    --role $LAMBDA_ROLE_ARN \
    --handler lambda_s3_redshift_automation.lambda_handler \
    --zip-file fileb://../lambda-deployment-package.zip \
    --timeout 900 \
    --memory-size 1024 \
    --description "Automated S3 to Redshift data pipeline"
```

### 3. Configure Environment Variables

```bash
# Get Redshift cluster identifier and IAM role ARN
REDSHIFT_CLUSTER_ID="my-redshift-cluster"
REDSHIFT_ROLE_ARN=$(aws iam get-role \
    --role-name redshift-s3-copy-role \
    --query 'Role.Arn' --output text)

# Set environment variables
aws lambda update-function-configuration \
    --function-name s3-redshift-automation \
    --environment Variables="{
        REDSHIFT_CLUSTER_ID=$REDSHIFT_CLUSTER_ID,
        REDSHIFT_DATABASE=dev,
        REDSHIFT_USER=awsuser,
        REDSHIFT_SCHEMA=public,
        IAM_ROLE_ARN=$REDSHIFT_ROLE_ARN
    }"
```

### 4. Create Dead Letter Queue

```bash
# Create SQS queue for failed messages
aws sqs create-queue \
    --queue-name s3-redshift-dlq \
    --attributes VisibilityTimeoutSeconds=300,MessageRetentionPeriod=1209600

# Get queue ARN
DLQ_ARN=$(aws sqs get-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/your-account-id/s3-redshift-dlq \
    --attribute-names QueueArn \
    --query 'Attributes.QueueArn' --output text)

# Configure Lambda to use DLQ
aws lambda update-function-configuration \
    --function-name s3-redshift-automation \
    --dead-letter-config TargetArn=$DLQ_ARN
```

## 🔗 Configure S3 Event Notifications

### 1. Grant S3 Permission to Invoke Lambda

```bash
# Get Lambda function ARN
LAMBDA_ARN=$(aws lambda get-function \
    --function-name s3-redshift-automation \
    --query 'Configuration.FunctionArn' --output text)

# Add permission for S3 to invoke Lambda
aws lambda add-permission \
    --function-name s3-redshift-automation \
    --principal s3.amazonaws.com \
    --action lambda:InvokeFunction \
    --statement-id s3-trigger-permission \
    --source-arn arn:aws:s3:::$BUCKET_NAME
```

### 2. Configure S3 Event Notification

Create `s3-event-config.json`:

```json
{
  "LambdaConfigurations": [
    {
      "Id": "s3-redshift-automation-trigger",
      "LambdaFunctionArn": "LAMBDA_ARN_PLACEHOLDER",
      "Events": ["s3:ObjectCreated:Put"],
      "Filter": {
        "Key": {
          "FilterRules": [
            {
              "Name": "prefix",
              "Value": "parquet-data/"
            },
            {
              "Name": "suffix",
              "Value": ".parquet"
            }
          ]
        }
      }
    }
  ]
}
```

Apply the configuration:

```bash
# Replace placeholder with actual Lambda ARN
sed "s/LAMBDA_ARN_PLACEHOLDER/$LAMBDA_ARN/g" s3-event-config.json > s3-event-config-final.json

# Apply S3 event notification configuration
aws s3api put-bucket-notification-configuration \
    --bucket $BUCKET_NAME \
    --notification-configuration file://s3-event-config-final.json
```

## 📊 Configure Monitoring

### 1. Create CloudWatch Dashboard

Create `cloudwatch-dashboard.json`:

```json
{
  "widgets": [
    {
      "type": "metric",
      "x": 0,
      "y": 0,
      "width": 12,
      "height": 6,
      "properties": {
        "metrics": [
          ["AWS/Lambda", "Duration", "FunctionName", "s3-redshift-automation"],
          [".", "Errors", ".", "."],
          [".", "Invocations", ".", "."]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-1",
        "title": "Lambda Performance Metrics",
        "period": 300
      }
    }
  ]
}
```

Create the dashboard:

```bash
aws cloudwatch put-dashboard \
    --dashboard-name S3RedshiftPipeline \
    --dashboard-body file://cloudwatch-dashboard.json
```

### 2. Create CloudWatch Alarms

```bash
# Create alarm for Lambda errors
aws cloudwatch put-metric-alarm \
    --alarm-name "S3RedshiftPipeline-Lambda-Errors" \
    --alarm-description "Lambda function error rate alarm" \
    --metric-name Errors \
    --namespace AWS/Lambda \
    --statistic Sum \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --dimensions Name=FunctionName,Value=s3-redshift-automation

# Create alarm for Lambda duration
aws cloudwatch put-metric-alarm \
    --alarm-name "S3RedshiftPipeline-Lambda-Duration" \
    --alarm-description "Lambda function duration alarm" \
    --metric-name Duration \
    --namespace AWS/Lambda \
    --statistic Average \
    --period 300 \
    --evaluation-periods 2 \
    --threshold 300000 \
    --comparison-operator GreaterThanThreshold \
    --dimensions Name=FunctionName,Value=s3-redshift-automation
```

## 🧪 Testing the Pipeline

### 1. Generate Test Data

```bash
# Generate sample orders
python scripts/order_generator.py --count 10 --output sample-data/

# Convert to parquet
python scripts/json_to_parquet.py --input sample-data/sample_order.json
```

### 2. Upload Test Files

```bash
# Create test directory in S3
aws s3api put-object \
    --bucket $BUCKET_NAME \
    --key parquet-data/

# Upload parquet files
aws s3 sync parquet_files/ s3://$BUCKET_NAME/parquet-data/
```

### 3. Monitor Processing

```bash
# Check Lambda logs
aws logs describe-log-groups \
    --log-group-name-prefix "/aws/lambda/s3-redshift-automation"

# Tail Lambda logs
aws logs tail /aws/lambda/s3-redshift-automation --follow

# Check CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=s3-redshift-automation \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 300 \
    --statistics Sum
```

### 4. Verify Results in Redshift

```sql
-- Connect to Redshift and check results
psql -h your-cluster-endpoint -U awsuser -d dev -p 5439

-- Check if tables were created
\dt

-- View sample data
SELECT * FROM public.order_summary LIMIT 5;
SELECT * FROM public.order_items LIMIT 5;

-- Check load timestamps
SELECT
    table_name,
    MAX(load_timestamp) as last_loaded,
    COUNT(*) as row_count
FROM (
    SELECT 'order_summary' as table_name, load_timestamp FROM public.order_summary
    UNION ALL
    SELECT 'order_items' as table_name, load_timestamp FROM public.order_items
) combined
GROUP BY table_name;
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Lambda Function Not Triggering

**Symptoms**: Files uploaded to S3 but Lambda doesn't execute

**Checks**:

```bash
# Verify S3 event configuration
aws s3api get-bucket-notification-configuration --bucket $BUCKET_NAME

# Check Lambda permissions
aws lambda get-policy --function-name s3-redshift-automation

# Verify file is in correct location with .parquet extension
aws s3 ls s3://$BUCKET_NAME/parquet-data/ --recursive
```

**Solutions**:

- Ensure files are uploaded to `parquet-data/` prefix
- Verify files have `.parquet` extension
- Check S3 event configuration matches Lambda ARN

#### 2. Lambda Execution Errors

**Symptoms**: Lambda function invoked but fails during execution

**Checks**:

```bash
# Check detailed Lambda logs
aws logs filter-log-events \
    --log-group-name /aws/lambda/s3-redshift-automation \
    --start-time $(date -d '1 hour ago' +%s)000 \
    --filter-pattern "ERROR"

# Check Lambda function configuration
aws lambda get-function-configuration --function-name s3-redshift-automation
```

**Common Solutions**:

- Increase Lambda timeout (current: 900 seconds)
- Increase Lambda memory (current: 1024 MB)
- Check environment variables are set correctly
- Verify IAM permissions for Redshift access

#### 3. Redshift Connection Issues

**Symptoms**: Lambda executes but fails to connect to Redshift

**Checks**:

```bash
# Test Redshift connectivity from local machine
psql -h your-cluster-endpoint -U awsuser -d dev -p 5439 -c "SELECT 1;"

# Check Redshift cluster status
aws redshift describe-clusters --cluster-identifier my-redshift-cluster
```

**Solutions**:

- Verify Redshift cluster is available and not in maintenance
- Check security group allows connections from Lambda
- Verify environment variables match cluster configuration
- Test with Redshift Data API permissions

#### 4. IAM Permission Issues

**Symptoms**: Access denied errors in Lambda logs

**Checks**:

```bash
# Verify Lambda execution role
aws iam get-role --role-name lambda-s3-redshift-execution-role

# Check attached policies
aws iam list-attached-role-policies --role-name lambda-s3-redshift-execution-role
aws iam list-role-policies --role-name lambda-s3-redshift-execution-role

# Test S3 access
aws s3 ls s3://$BUCKET_NAME/parquet-data/
```

**Solutions**:

- Verify S3 bucket policy allows Lambda role access
- Check Redshift IAM role has S3 read permissions
- Ensure Lambda role has Redshift Data API permissions

### Debug Commands

```bash
# Get recent Lambda executions
aws lambda list-functions --query 'Functions[?FunctionName==`s3-redshift-automation`]'

# Check Lambda function code
aws lambda get-function --function-name s3-redshift-automation

# View recent CloudWatch metrics
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Errors \
    --dimensions Name=FunctionName,Value=s3-redshift-automation \
    --start-time $(date -u -d '24 hours ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 3600 \
    --statistics Sum

# Check DLQ for failed messages
aws sqs get-queue-attributes \
    --queue-url https://sqs.us-east-1.amazonaws.com/your-account-id/s3-redshift-dlq \
    --attribute-names ApproximateNumberOfMessages
```

## 🔄 Updates and Maintenance

### Updating Lambda Function

```bash
# Package updated code
cd automation/
zip -r ../lambda-deployment-package-updated.zip .

# Update function code
aws lambda update-function-code \
    --function-name s3-redshift-automation \
    --zip-file fileb://../lambda-deployment-package-updated.zip

# Update configuration if needed
aws lambda update-function-configuration \
    --function-name s3-redshift-automation \
    --timeout 900 \
    --memory-size 1024
```

### Monitoring Health

```bash
# Create monitoring script
cat > monitor-pipeline.sh << 'EOF'
#!/bin/bash
echo "=== Pipeline Health Check ==="
echo "Lambda function status:"
aws lambda get-function --function-name s3-redshift-automation --query 'Configuration.[State,LastUpdateStatus]' --output table

echo "Recent invocations (last hour):"
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Invocations \
    --dimensions Name=FunctionName,Value=s3-redshift-automation \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 3600 \
    --statistics Sum \
    --query 'Datapoints[0].Sum'

echo "Recent errors (last hour):"
aws cloudwatch get-metric-statistics \
    --namespace AWS/Lambda \
    --metric-name Errors \
    --dimensions Name=FunctionName,Value=s3-redshift-automation \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 3600 \
    --statistics Sum \
    --query 'Datapoints[0].Sum'
EOF

chmod +x monitor-pipeline.sh
./monitor-pipeline.sh
```

## 📚 Next Steps

After successful setup:

1. **Review Documentation**: Read through [Complete Project Documentation](docs/COMPLETE_PROJECT_DOCUMENTATION.md)
2. **Explore Architecture**: Study [Architecture Diagrams](docs/ARCHITECTURE_DIAGRAMS.md)
3. **Understand Implementation**: Review [Technical Implementation Summary](docs/TECHNICAL_IMPLEMENTATION_SUMMARY.md)
4. **Set Up Monitoring**: Configure additional CloudWatch dashboards and alerts
5. **Plan Production Deployment**: Consider multi-environment setup and CI/CD pipeline

## 🆘 Support

If you encounter issues during setup:

1. Check the [Troubleshooting](#-troubleshooting) section above
2. Review AWS service quotas and limits
3. Verify all prerequisites are met
4. Check AWS CloudTrail for API call errors
5. Create a GitHub issue with detailed error information

---

**Setup Complete!** 🎉

Your S3 to Redshift automated data pipeline is now ready for use. Upload parquet files to your S3 bucket's `parquet-data/` prefix and watch them automatically appear in your Redshift cluster!
