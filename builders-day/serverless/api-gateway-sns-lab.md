# API Gateway to SNS Email Lab
**AWS Certified Cloud Practitioner / Associate Level**  
Build a REST API that sends email notifications through SNS using API Gateway direct integration.

---

## Lab Overview
Build a REST API with API Gateway that:
1. **Mock endpoint** (GET /) returns success response
2. **Send message endpoint** (POST /send-message) publishes to SNS
3. **Email delivery** through SNS subscription

**Architecture Flow:**
```
API Gateway (GET /) → Mock Response
API Gateway (POST /send-message) → SNS Topic → Email
```

**Why this architecture?**
- **Serverless**: No Lambda functions needed for simple operations
- **Direct integration**: API Gateway directly invokes SNS
- **Cost-effective**: Pay only for API calls and SNS publishes
- **Simple**: Fewer moving parts, easier to maintain

---

## Prerequisites
- AWS account with Administrator access
- **Web browser** with access to AWS Management Console
- **Email address** for SNS notifications
- **Region**: All tasks must be done in **us-west-2** for consistency

---

## Task 1: SNS Topic Setup

### Step 1: Create SNS Topic
1. **Navigate** to SNS service
2. **Click** "Topics" → "Create topic"
3. **Type**: Standard
4. **Name**: `APIGatewayNotifications`
5. **Click "Create topic"**
6. **Copy the Topic ARN** - you'll need this later (e.g., `arn:aws:sns:us-west-2:123456789012:APIGatewayNotifications`)

### Step 2: Subscribe Email to SNS Topic
1. In the topic details page, **click** "Create subscription"
2. **Protocol**: Email
3. **Endpoint**: Your email address
4. **Click "Create subscription"**
5. **Check your email** and click confirmation link
6. **Verify** subscription status shows "Confirmed"

---

## Task 2: IAM Role for API Gateway

### Step 1: Create IAM Role
1. **Navigate** to IAM service
2. **Click** "Roles" → "Create role"
3. **Select** "AWS service" → "API Gateway"
4. **Click "Next"**
5. **Click "Create policy"** (opens in new tab)

### Step 2: Create SNS Publish Policy
1. In the new tab, **click** "JSON" tab
2. **Paste** this policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sns:Publish",
            "Resource": "arn:aws:sns:us-west-2:*:APIGatewayNotifications"
        }
    ]
}
```
3. **Click "Next"**
4. **Policy name**: `APIGateway-SNS-Publish`
5. **Click "Create policy"**

### Step 3: Attach Policy to Role
1. **Return to the role creation tab** (refresh policy list if needed)
2. **Search** for `APIGateway-SNS-Publish`
3. **Select** the policy checkbox
4. **Click "Next"**
5. **Role name**: `APIGateway-SNS-Role`
6. **Click "Create role"**
7. **Click** on the newly created role
8. **Copy the Role ARN** - you'll need this later

---

## Task 3: Create REST API

### Step 1: Create API Gateway
1. **Navigate** to API Gateway service
2. **Click** "Create API"
3. **Choose** "REST API" (not Private or HTTP API)
4. **Click "Build"**
5. **Protocol**: REST
6. **Create new API**: New API
7. **API name**: `NotificationAPI`
8. **Endpoint Type**: Regional
9. **Click "Create API"**

---

## Task 4: Configure Mock Endpoint (GET /)

### Step 1: Setup Mock Integration
1. **Select** the "/" resource (root)
2. **Click** "Create Method"
3. **Method type**: GET
4. **Click** checkmark or "Create method"
5. **Integration type**: Mock
6. **Click "Save"**

**Note**: The mock integration will automatically return a 200 OK response. No additional configuration needed.

---

## Task 5: Configure SNS Endpoint (POST /send-message)

### Step 1: Create Resource
1. **Click** "Resources" in left sidebar
2. **Select** "/" resource
3. **Click** "Create Resource"
4. **Resource Name**: send-message
5. **Resource Path**: /send-message
6. **Click "Create Resource"**

### Step 2: Create POST Method
1. **Select** the "/send-message" resource
2. **Click** "Create Method"
3. **Method type**: POST
4. **Integration type**: AWS Service
5. **AWS Region**: us-west-2
6. **AWS Service**: Simple Notification Service (SNS)
7. **AWS Subdomain**: Leave empty
8. **HTTP method**: POST
9. **Action Type**: Use action name
10. **Action**: Publish
11. **Execution role**: Paste the IAM Role ARN from Task 2 (e.g., `arn:aws:iam::123456789012:role/APIGateway-SNS-Role`)
12. **Click "Save"**

### Step 3: Configure Integration Request
1. **Click** "Integration Request"
2. **Scroll down** to "URL Query String Parameters"
3. **Click** "Add query string parameter"
4. **Configure TopicArn parameter**:
   - **Name**: TopicArn
   - **Mapped from**: `'arn:aws:sns:us-west-2:YOUR_ACCOUNT_ID:APIGatewayNotifications'`
   - **Replace** `YOUR_ACCOUNT_ID` with your actual AWS account ID
   - **Click** checkmark
5. **Click** "Add query string parameter" again
6. **Configure Message parameter**:
   - **Name**: Message
   - **Mapped from**: `method.request.body`
   - **Click** checkmark
7. **Click "Save"** (top right)

**Note**: Integration response is automatically configured. SNS will return an XML response when successful.

---

## Task 6: Deploy API

### Step 1: Create Deployment
1. **Click** "Deploy API" button (top right or Actions dropdown)
2. **Deployment stage**: [New Stage]
3. **Stage name**: dev
4. **Click "Deploy"**

### Step 2: Get Invoke URL
1. **Click** "Stages" in left sidebar
2. **Expand** "dev" stage
3. **Click** on "dev" to see stage details
4. **Copy the "Invoke URL"** at the top (e.g., `https://abc123.execute-api.us-west-2.amazonaws.com/dev`)

---

## Task 7: Test the API

### Step 1: Test Mock Endpoint
1. **Open** CloudShell (icon in top navigation bar)
2. **Run** this command (replace with your invoke URL):
```bash
curl -X GET https://YOUR_INVOKE_URL/dev/
```
3. **Expected response**: Empty body with HTTP 200 status (you can add `-v` flag to see status code)

### Step 2: Test SNS Endpoint
1. **In CloudShell**, run this command (replace with your invoke URL):
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"Message": "Hello from API Gateway!"}' \
  https://YOUR_INVOKE_URL/dev/send-message
```
2. **Expected response**: XML response from SNS with HTTP 200 status

### Step 3: Verify Email Delivery
1. **Check your email** for the SNS notification
2. **Subject**: AWS Notification Message
3. **Body**: Should contain "Hello from API Gateway!"

### Step 4: Test with Different Messages
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"Message": "Testing API Gateway to SNS integration"}' \
  https://YOUR_INVOKE_URL/dev/send-message
```

---

## Verification Checklist

### Task 1: SNS Configuration
- ✅ SNS topic created
- ✅ Email subscription confirmed

### Task 2: IAM Configuration
- ✅ Policy created with SNS publish permission
- ✅ Role created for API Gateway

### Task 3: API Gateway Created
- ✅ REST API created with regional endpoint

### Task 4: Mock Endpoint
- ✅ GET / method configured with mock integration

### Task 5: SNS Endpoint
- ✅ /send-message resource created
- ✅ POST method with AWS Service integration
- ✅ URL query string parameters configured (TopicArn and Message)

### Task 6: API Deployment
- ✅ API deployed to dev stage
- ✅ Invoke URL obtained

### Task 7: Testing
- ✅ Mock endpoint returns success
- ✅ SNS endpoint accepts POST requests
- ✅ Email notification received

---

## Troubleshooting

### Issue: 403 Forbidden on /send-message
**Check:**
1. IAM role ARN is correct in the POST method integration
2. IAM role has `sns:Publish` permission
3. Topic ARN in URL query string parameters is correct
4. Account ID in Topic ARN matches your account

### Issue: No email received
**Check:**
1. Email subscription is "Confirmed" status
2. Check spam/junk folder
3. Topic ARN in URL query string parameters is correct
4. Check SNS topic metrics for successful publishes

### Issue: 502 Bad Gateway
**Check:**
1. Action name is "Publish" (case-sensitive)
2. URL query string parameters are configured correctly
3. Both TopicArn and Message parameters are present
4. TopicArn is wrapped in single quotes

### Issue: Empty message in email
**Check:**
1. Message parameter is mapped from `method.request.body`
2. Curl command includes `-d` flag with message content
3. Request body is not empty

---

## Architecture Benefits

### Direct Integration
- **No Lambda needed**: API Gateway directly invokes SNS
- **Reduced latency**: Fewer hops in request path
- **Lower costs**: No Lambda invocation charges

### Serverless
- **Auto-scaling**: Handles any request volume
- **No servers**: Fully managed services
- **High availability**: Built-in redundancy

### Security
- **IAM roles**: Secure authentication between services
- **Least privilege**: Role only has SNS publish permission
- **API throttling**: Built-in DDoS protection

---

## Cleanup

### Step 1: Delete API Gateway
1. **Navigate** to API Gateway service
2. **Select** `NotificationAPI`
3. **Actions** → "Delete API"
4. **Type** the API name to confirm
5. **Click "Delete"**

### Step 2: Delete SNS Resources
1. **Navigate** to SNS service
2. **Click** "Subscriptions" → Select your email subscription → "Delete"
3. **Click** "Topics" → Select `APIGatewayNotifications` → "Delete"

### Step 3: Delete IAM Resources
1. **Navigate** to IAM → Roles
2. **Select** `APIGateway-SNS-Role` → "Delete"
3. **Navigate** to IAM → Policies
4. **Select** `APIGateway-SNS-Publish` → "Actions" → "Delete"

---

## Key Takeaways

### API Gateway Integration Types
| Type | Use Case |
|------|----------|
| **Mock** | Testing, placeholder endpoints |
| **AWS Service** | Direct integration with AWS services |
| **Lambda** | Custom business logic |
| **HTTP** | Proxy to external APIs |

### URL Query String Parameters
- **Purpose**: Map request data to backend service parameters
- **Syntax**: Use `method.request.body` for full body, `method.request.querystring.param` for query params
- **Static values**: Wrap in single quotes (e.g., `'static-value'`)

### Best Practices Demonstrated
- ✅ **IAM least privilege**: Role only has required permissions
- ✅ **Resource-based policies**: SNS topic ARN restriction
- ✅ **Direct parameter mapping**: Simple request transformation
- ✅ **Regional endpoints**: Lower latency, better availability

### Real-World Applications
- **Notification systems**: Alert users via email/SMS
- **Contact forms**: Website contact forms without backend servers
- **Monitoring alerts**: External systems sending alerts
- **Webhook receivers**: Receive notifications from third-party services

---

## Extension Ideas

### 1. Add Request Validation
- Add request model schema
- Validate message format before sending
- Return 400 for invalid requests

### 2. Add SMS Support
- Modify SNS integration to support phone numbers
- Add parameter for notification type
- Route to appropriate SNS protocol

### 3. Add Authentication
- Configure API Gateway authorizer
- Use API keys for access control
- Add usage plans and throttling

### 4. Add Multiple Topics
- Accept topic parameter in request body or query string
- Add TopicArn as `method.request.querystring.topic`
- Route to different SNS topics dynamically

---

## Resources
- [API Gateway REST API Documentation](https://docs.aws.amazon.com/apigateway/latest/developerguide/apigateway-rest-api.html)
- [API Gateway AWS Service Integration](https://docs.aws.amazon.com/apigateway/latest/developerguide/integration-request-basic-setup.html)
- [Amazon SNS Developer Guide](https://docs.aws.amazon.com/sns/)
- [API Gateway Request Parameters](https://docs.aws.amazon.com/apigateway/latest/developerguide/request-response-data-mappings.html)

---

**🎯 Learning Objectives Achieved:**
- ✅ Build REST API with API Gateway
- ✅ Configure mock integration for testing
- ✅ Implement AWS Service direct integration
- ✅ Create IAM roles for service-to-service communication
- ✅ Use URL query string parameters for request transformation
- ✅ Test APIs using CloudShell
- ✅ Integrate API Gateway with SNS for notifications


