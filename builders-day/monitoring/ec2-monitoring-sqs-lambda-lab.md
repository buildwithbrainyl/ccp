# EC2 Monitoring with SQS & Lambda Lab
**AWS Certified Cloud Practitioner / Associate Level**  
Learn event-driven EC2 automation using CloudWatch, SNS, SQS, and Lambda - all through the AWS Management Console.

---

## Lab Overview
Build an event-driven EC2 monitoring system that:
1. **Monitors EC2 CPU** with CloudWatch alarms
2. **Publishes alerts** to SNS topic
3. **Queues messages** in SQS for reliable processing
4. **Processes automatically** with Lambda to stop EC2

**Architecture Flow:**
```
EC2 Instance → CloudWatch Alarm → SNS Topic → SQS Queue → Lambda Function → Stop EC2
```

**Why this architecture?**
- **Decoupling**: SNS and SQS decouple alarm from action
- **Reliability**: SQS ensures messages aren't lost
- **Scalability**: Lambda scales automatically
- **Fault tolerance**: Failed Lambda invocations can be retried

---

## Prerequisites
- AWS account with Administrator access
- **Web browser** with access to AWS Management Console
- **Email address** for SNS notifications
- **Region**: All tasks must be done in **us-west-2** for consistency

---

## Task 1: EC2 Setup with CloudWatch Agent

### Step 1: Create IAM Role for EC2
1. **Navigate** to IAM service
2. **Click** "Roles" → "Create role"
3. **Select** "AWS service" → "EC2"
4. **Click "Next"** → **Attach policies**:
   - Search and select `CloudWatchAgentServerPolicy`
5. **Role name**: `EC2-CloudWatch-Role`
6. **Click "Create role"**

### Step 2: Launch EC2 Instance
1. **Navigate** to EC2 service → **Click "Launch Instance"**
2. **Configuration**:
   - **Name**: `MonitoredServer`
   - **AMI**: Amazon Linux 2023 AMI
   - **Instance type**: t3.micro
   - **Key pair**: Proceed without a key pair (not needed)
   - **Security group**: Create new with default settings
   - **IAM instance profile**: Select `EC2-CloudWatch-Role`
3. **Click "Launch instance"**
4. **Wait** for instance to reach "Running" state
5. **Note the Instance ID** (e.g., `i-0123456789abcdef0`) - you'll need this later

---

## Task 2: SNS Topic & Email Subscription

### Step 1: Create SNS Topic
1. **Navigate** to SNS service
2. **Click** "Topics" → "Create topic"
3. **Type**: Standard
4. **Name**: `EC2-CPU-Alerts`
5. **Click "Create topic"**
6. **Copy the Topic ARN** - you'll need this later

### Step 2: Subscribe Email to SNS Topic
1. In the topic details page, **click** "Create subscription"
2. **Protocol**: Email
3. **Endpoint**: Your email address
4. **Click "Create subscription"**
5. **Check your email** and click confirmation link

---

## Task 3: SQS Queue Setup

### Step 1: Create SQS Queue
1. **Navigate** to SQS service
2. **Click** "Create queue"
3. **Type**: Standard
4. **Name**: `EC2-Alarm-Queue`
5. **Configuration** (scroll down):
   - **Visibility timeout**: 60 seconds
   - **Message retention period**: 4 days (default)
   - **Delivery delay**: 0 seconds
   - **Maximum message size**: 1024 KB (default)
6. **Click "Create queue"**
7. **Copy the Queue ARN** from the details page

### Step 2: Subscribe SQS Queue to SNS Topic
1. **Stay in SQS console** on your queue details page
2. **Click** "SNS subscriptions" tab
3. **Click** "Subscribe to Amazon SNS topic"
4. **Choose** the `EC2-CPU-Alerts` topic from dropdown
5. **Click "Save"**
6. **Verify** subscription appears in the list

---

## Task 4: Lambda Function Setup

### Step 1: Create IAM Role for Lambda
1. **Navigate** to IAM service
2. **Click** "Roles" → "Create role"
3. **Select** "AWS service" → "Lambda"
4. **Click "Next"** → **Attach policies**:
   - Search and select `AWSLambdaSQSQueueExecutionRole`
   - Search and select `AmazonEC2FullAccess`
5. **Role name**: `Lambda-EC2-Stop-Role`
6. **Click "Create role"**

### Step 2: Create Lambda Function
1. **Navigate** to Lambda service
2. **Click** "Create function"
3. **Select** "Author from scratch"
4. **Configuration**:
   - **Function name**: `StopEC2OnAlarm`
   - **Runtime**: Python 3.12
   - **Architecture**: x86_64
   - **Permissions**: Use an existing role → Select `Lambda-EC2-Stop-Role`
5. **Click "Create function"**

### Step 3: Add Lambda Function Code
1. **In the Code tab**, delete the default code
2. **Copy the code** from this link:  
   [https://github.com/buildwithbrainyl/ccp/blob/main/materials/stop_ec2_lambda.py](https://github.com/buildwithbrainyl/ccp/blob/main/materials/stop_ec2_lambda.py)
3. **Paste** into the code editor (lambda_function.py)
4. **Click "Deploy"**

### Step 4: Configure Environment Variable
1. **Click** "Configuration" tab → "Environment variables"
2. **Click** "Edit" → "Add environment variable"
3. **Key**: `INSTANCE_ID`
4. **Value**: Your EC2 instance ID (from Task 1, Step 2)
5. **Click "Save"**

---

## Task 5: Configure SQS to Trigger Lambda

### Step 1: Configure Lambda Trigger from SQS
1. **Navigate** to SQS service
2. **Select** the `EC2-Alarm-Queue` queue
3. **Click** "Lambda triggers" tab
4. **Click** "Configure Lambda function trigger"
5. **Lambda function**: Select `StopEC2OnAlarm` from dropdown
6. **Click "Save"**
7. **Verify** the trigger appears in the Lambda triggers list

---

## Task 6: CloudWatch Alarm Configuration

### Step 1: Create CloudWatch Alarm
1. **Navigate** to CloudWatch service
2. **Click** "Alarms" → "All alarms" → "Create alarm"
3. **Click** "Select metric"
4. **Choose** "EC2" → "Per-Instance Metrics"
5. **Find** your `MonitoredServer` instance
6. **Select** the "CPUUtilization" metric
7. **Click "Select metric"**

### Step 2: Configure Alarm Conditions
1. **Statistic**: Average
2. **Period**: 5 minutes
3. **Threshold type**: Static
4. **Condition**: Greater/Equal (≥) **80**
5. **Click "Next"**

### Step 3: Configure Alarm Actions
1. **Alarm state trigger**: In alarm
2. **SNS topic**: Select existing → `EC2-CPU-Alerts`
3. **Click "Next"**

### Step 4: Complete Alarm Setup
1. **Alarm name**: `High-CPU-Alert`
2. **Description**: `Triggers when CPU exceeds 80% - stops instance via Lambda`
3. **Click "Next"** → Review → **"Create alarm"**

---

## Task 7: Test the Complete Architecture

### Step 1: Test with CloudShell
1. **Open** CloudShell (icon in top navigation bar)
2. **Run** the following command to trigger the alarm:
```bash
aws cloudwatch set-alarm-state \
  --alarm-name "High-CPU-Alert" \
  --state-value ALARM \
  --state-reason "Testing complete architecture"
```

### Step 2: Monitor the Flow
1. **Navigate to CloudWatch Metrics** → SNS Topic"
   - Verify the NumberOfMessagesPublished metric

2. **Navigate to SQS** → Queues → `EC2-Alarm-Queue` → "Monitoring"
   - Check "Messages received" graph for spike
   - Check "Messages deleted" showing Lambda processed it

3. **Navigate to Lambda** → Functions → `StopEC2OnAlarm` → "Monitor"
   - Click "Logs" tab → View CloudWatch Logs
   - Verify logs show: "Stopping instance i-xxxxx..."

4. **Navigate to EC2** → Instances
   - Verify `MonitoredServer` is **stopped** or **stopping**

5. **Check your email**
   - Verify you received alarm notification from SNS

### Step 3: Verify Lambda Logs
1. **In Lambda console**, click "Monitor" tab → "View CloudWatch logs"
2. **Click** on the latest log stream
3. **Look for these log entries**:
   - "Event:" showing the SQS message
   - "Stopping instance i-xxxxx..."
   - "StopInstances called for i-xxxxx"

---

## Verification Checklist

### Task 1: EC2 Setup
- ✅ EC2 instance launched with CloudWatch role
- ✅ Instance ID noted for later use

### Task 2: SNS Configuration
- ✅ SNS topic created
- ✅ Email subscription confirmed

### Task 3: SQS Configuration
- ✅ SQS queue created
- ✅ Queue subscribed to SNS topic

### Task 4: Lambda Configuration
- ✅ Lambda function created with proper IAM role
- ✅ Function code deployed from GitHub
- ✅ Environment variable set with instance ID

### Task 5: SQS Trigger Configuration
- ✅ Lambda trigger configured from SQS console
- ✅ Trigger verified in Lambda triggers list

### Task 6: CloudWatch Alarm
- ✅ Alarm created monitoring CPU utilization
- ✅ Alarm configured to publish to SNS

### Task 7: End-to-End Test
- ✅ Alarm triggered via CloudShell
- ✅ SNS published message
- ✅ SQS received and delivered message to Lambda
- ✅ Lambda successfully stopped EC2 instance
- ✅ Email notification received

---

## Troubleshooting

### Issue: Lambda not triggered
**Check:**
1. SQS Lambda trigger is properly configured (check SQS → Lambda triggers tab)
2. Lambda role has `AWSLambdaSQSQueueExecutionRole` policy
3. Check SQS queue for messages in "Messages available"
4. Verify queue subscription to SNS topic is active

### Issue: Lambda fails to stop instance
**Check:**
1. Environment variable `INSTANCE_ID` is set correctly
2. Lambda role has `AmazonEC2FullAccess` policy
3. Instance is in a stoppable state (not terminated)
4. View Lambda CloudWatch logs for error details

### Issue: No SNS notification received
**Check:**
1. Email subscription is "Confirmed" (not "Pending confirmation")
2. Check spam/junk folder
3. Alarm actually triggered (check alarm history in CloudWatch)

---

## Architecture Benefits

### Decoupling
- **SNS** separates alarm from processing logic
- **SQS** acts as buffer between SNS and Lambda
- Changes to Lambda don't affect alarm configuration

### Reliability
- **SQS persistence**: Messages retained up to 14 days
- **Automatic retries**: Lambda retries failed invocations
- **Dead Letter Queue**: Can be added for failed messages

### Scalability
- **Lambda auto-scales**: Handles bursts of alarms automatically
- **SQS buffering**: Smooths out traffic spikes
- **Multiple consumers**: Can add more Lambda functions

### Cost Efficiency
- **Pay per use**: No idle infrastructure costs
- **Efficient batching**: Process multiple alarms together
- **No server management**: Fully serverless architecture

---

## Cleanup

### Step 1: Delete CloudWatch Alarm
1. **Navigate** to CloudWatch → Alarms
2. **Select** `High-CPU-Alert`
3. **Actions** → "Delete"

### Step 2: Delete Lambda Function
1. **Navigate** to Lambda → Functions
2. **Select** `StopEC2OnAlarm`
3. **Actions** → "Delete"

### Step 3: Delete SQS Queue
1. **Navigate** to SQS → Queues
2. **Select** `EC2-Alarm-Queue`
3. **Actions** → "Delete"

### Step 4: Delete SNS Resources
1. **Navigate** to SNS → Topics
2. **Select** `EC2-CPU-Alerts`
3. **Delete** email subscription first
4. **Delete** topic

### Step 5: Terminate EC2 Instance
1. **Navigate** to EC2 → Instances
2. **Select** `MonitoredServer`
3. **Instance State** → "Terminate instance"

### Step 6: Delete IAM Roles
1. **Navigate** to IAM → Roles
2. **Delete** these roles:
   - `EC2-CloudWatch-Role`
   - `Lambda-EC2-Stop-Role`

---

## Key Takeaways

### Event-Driven Architecture
- **Asynchronous processing**: Components work independently
- **Loose coupling**: Easy to modify without breaking other parts
- **Resilience**: Failures in one component don't cascade

### AWS Services Integration
| Service | Purpose in Architecture |
|---------|------------------------|
| **CloudWatch** | Monitoring and alarming |
| **SNS** | Fan-out notifications to multiple subscribers |
| **SQS** | Reliable message queuing and buffering |
| **Lambda** | Serverless compute for automated actions |
| **EC2** | The monitored and controlled resource |

### Best Practices Demonstrated
- ✅ **IAM least privilege**: Each role has only needed permissions
- ✅ **Environment variables**: Configuration separate from code
- ✅ **Structured logging**: Lambda logs for debugging and audit
- ✅ **Error handling**: Lambda code handles malformed messages
- ✅ **Message validation**: Extract instance ID from alarm payload
- ✅ **Idempotency**: Lambda checks instance state before stopping

### Real-World Applications
- **Auto-scaling**: Stop unused instances to save costs
- **Incident response**: Automatically remediate security issues
- **Cost optimization**: Shutdown non-production environments
- **Compliance**: Enforce policies with automated actions

---

## Extension Ideas

### 1. Add Dead Letter Queue (DLQ)
- Create another SQS queue for failed messages
- Configure on `EC2-Alarm-Queue` settings
- Analyze failed messages for debugging

### 2. Multi-Action Response
- Modify Lambda to take different actions based on alarm severity
- Add SNS notification after successful stop
- Log actions to DynamoDB for audit trail

### 3. Schedule-Based Control
- Add EventBridge rule to start instances on schedule
- Combine with cost optimization policies
- Create full lifecycle management

### 4. Multi-Instance Support
- Remove `INSTANCE_ID` environment variable
- Rely solely on alarm dimension parsing
- Monitor multiple instances with same Lambda

---

## Resources
- [Lambda Function Code (GitHub)](https://github.com/buildwithbrainyl/ccp/blob/main/materials/stop_ec2_lambda.py)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [Amazon SQS Developer Guide](https://docs.aws.amazon.com/sqs/)
- [Amazon SNS Developer Guide](https://docs.aws.amazon.com/sns/)
- [Amazon CloudWatch User Guide](https://docs.aws.amazon.com/cloudwatch/)

---

**🎯 Learning Objectives Achieved:**
- ✅ Build event-driven serverless architecture
- ✅ Integrate CloudWatch, SNS, SQS, and Lambda
- ✅ Configure SQS as Lambda event source
- ✅ Process CloudWatch alarm messages in Lambda
- ✅ Implement automated EC2 lifecycle management
- ✅ Apply AWS best practices for monitoring and automation
